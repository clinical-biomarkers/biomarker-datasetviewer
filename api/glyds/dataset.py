import os,sys
from flask_restx import Namespace, Resource, fields
from flask import (request, current_app)
from glyds.document import get_one, get_many, get_many_text_search, get_ver_list, order_json_obj
from werkzeug.utils import secure_filename
from glyds.qc import run_qc
import datetime
import time
import subprocess
import json
import pytz
import hashlib
from glyds.db import get_mongodb



api = Namespace("dataset", description="Dataset APIs")

dataset_getall_query_model = api.model(
    'Dataset Get All Query', 
    {
    }
)

download_query_model = api.model(
    "List Download Query",
    {
        "id": fields.String(required=True, default=""),
        "format": fields.String(required=True, default="csv")
    }
)


dataset_search_query_model = api.model(
    'Dataset Search Query',
    {
        'query': fields.String(required=True, default="", description='Query string')
    }
)



dataset_list_query_model = api.model(
    'Dataset List Query',
    {
        'list_id': fields.String(required=True, default="", description='List ID string')
    }
)



dataset_historylist_query_model = api.model(
    'Dataset History List Query',
    {
        'query': fields.String(required=True, default="", description='Query string')
    }
)

dataset_detail_query_model = api.model(
    'Dataset Detail Query',
    {
        'bcoid': fields.String(required=True, default="GLY_000001", description='BCO ID'),
        'dataversion': fields.String(required=False, default="1.12.1", description='Dataset Release [e.g: 1.12.1]'),
    }
)

dataset_upload_query_model = api.model(
    'Dataset Upload Query',
    {
        "format":fields.String(required=True, default="", description='File Format [csv/tsv]'),
        "qctype":fields.String(required=True, default="", description='QC Type [basic/single_glyco_site]'),
        "dataversion":fields.String(required=True, default="", description='Data Release [e.g: 1.12.1]')
    }
)

dataset_submit_query_model = api.model(
    'Dataset Submit Query',
    {
        'fname': fields.String(required=True, default="", description='First name'),
        'lname': fields.String(required=True, default="", description='Last name'),
        'email': fields.String(required=True, default="", description='Email address'),
        'affilation': fields.String(required=True, default="", description='Affilation')
    }
)

glycan_finder_query_model = api.model(
    'Glycan Finder Query',
    {
        'filename': fields.String(required=True, default="", description='File name')
    }
)

dataset_historydetail_query_model = api.model(
    'Dataset History Detail Query',
    {
        'bcoid': fields.String(required=True, default="GLY_000001", description='BCO ID')
    }
)

pagecn_query_model = api.model(
    'Dataset Page Query',
    {
        'pageid': fields.String(required=True, default="faq", description='Page ID')
    }
)

init_query_model = api.model(
    'Init Query',
    {
    }
)


ds_model = api.model('Dataset', {
    'id': fields.String(readonly=True, description='Unique dataset identifier'),
    'title': fields.String(required=True, description='Dataset title')
})





@api.route('/getall')
class DatasetGetAll(Resource):
    '''f dfdsfadsfas f '''
    @api.doc('getall_datasets')
    @api.expect(dataset_getall_query_model)
    def post(self):
        '''Get all datasets'''
        req_obj = request.json
        res_obj = {"recordlist":[]}
        r_one = get_many({"coll":"c_extract", "query":""})
        if "error" in r_one:
            return r_one
        
        for obj in r_one["recordlist"]:
            if "categories" in obj:
                if "tag" in obj["categories"]:
                    obj["categories"].pop("tag")

        res_obj["recordlist"] = r_one["recordlist"]
        n = len(res_obj["recordlist"])
        res_obj["stats"] = {"total":n, "retrieved":n}
        return res_obj





@api.route('/search')
class DatasetSearch(Resource):
    '''f dfdsfadsfas f '''
    @api.doc('search_datasets')
    @api.expect(dataset_search_query_model)
    #@api.marshal_list_with(ds_model)
    def post(self):
        '''Search datasets'''
       
        req_obj = request.json
        mongo_dbh, error_obj = get_mongodb()
        if error_obj != {}:
            return error_obj
       
        hash_str = json.dumps(req_obj)
        hash_obj = hashlib.md5(hash_str.encode('utf-8'))
        list_id = hash_obj.hexdigest()
               
        coll_names = mongo_dbh.collection_names()
        if "c_cache" in coll_names:
            res = get_one({"coll":"c_cache", "list_id":list_id})
            if "error" not in res:
                if "record" in res:
                    return {"list_id":list_id}

        res_obj = {"recordlist":[]}
        r_one = get_many({"coll":"c_extract", "query":""})
        if "error" in r_one:
            return r_one

        bco_dict = {}
        for obj in r_one["recordlist"]:
            bco_dict[obj["bcoid"]] = {"filename":obj["filename"],"categories":obj["categories"],
                "title":obj["title"]
            }

        if req_obj["query"] == "":
            res_obj["recordlist"] = r_one["recordlist"]
        else:
            #dataset body search
            req_obj["coll"] = "c_records"
            r_two = get_many_text_search(req_obj)
            if "error" in r_two:
                return r_two
            out_dict = {}
            for obj in r_two["recordlist"]:
                prefix, bco_idx, file_idx, row_idx = obj["recordid"].split("_")
                bco_id = prefix + "_" + bco_idx
                if bco_id not in bco_dict:
                    continue
                bco_title, file_name = bco_dict[bco_id]["title"], bco_dict[bco_id]["filename"]
                o = {
                    "recordid":obj["recordid"],
                    "bcoid":bco_id, "fileidx":file_idx,
                    "filename":file_name, "title":bco_title,
                    "categories":bco_dict[bco_id]["categories"],
                    "rowlist":[]
                }
                if bco_id not in out_dict:
                    out_dict[bco_id] = o
                out_dict[bco_id]["rowlist"].append(int(row_idx))
            for bco_id in sorted(out_dict):
                res_obj["recordlist"].append(out_dict[bco_id])
            

            #dataset metadata search
            seen = {}
            req_obj["coll"] = "c_bco"
            r_three = get_many_text_search(req_obj)
            if "error" in r_three:
                return r_three
            
            r_four = get_many(req_obj)
            if "error" in r_four:
                return r_four

            for doc in r_three["recordlist"] + r_four["recordlist"] :
                if "object_id" in doc:
                    bco_id = doc["object_id"].split("/")[-2]
                    seen[bco_id] = True
            for doc in r_one["recordlist"]:
                if doc["bcoid"] in seen and doc["bcoid"] not in out_dict:
                    res_obj["recordlist"].append(doc)


        n = len(res_obj["recordlist"])
        res_obj["stats"] = {"total":n, "retrieved":n}
        if n != 0:
            ts_format = "%Y-%m-%d %H:%M:%S %Z%z"
            ts = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime(ts_format)
            cache_info = { "reqobj":req_obj, "ts":ts}
            cache_obj = { "list_id":list_id, "cache_info":cache_info, "results":res_obj}
            cache_coll = "c_cache"
            res = mongo_dbh[cache_coll].insert_one(cache_obj)

    
        res_obj = {"list_id":list_id}
        return res_obj



@api.route('/list')
class DatasetList(Resource):
    '''Get search results'''
    @api.doc('get_dataset')
    @api.expect(dataset_list_query_model)
    #@api.marshal_with(ds_model)
    def post(self):
        '''Get search results'''
        req_obj = request.json
        req_obj["coll"] = "c_cache"
        res = get_one(req_obj)
        if "error" in res:
            return res
        res_obj = {
            "status":1, 
            "recordlist":res["record"]["results"]["recordlist"],
            "stats":res["record"]["results"]["stats"],
            "searchquery":res["record"]["cache_info"]["reqobj"]["query"]
        }
        return res_obj





@api.route('/detail')
class DatasetDetail(Resource):
    '''Show a single dataset item'''
    @api.doc('get_dataset')
    @api.expect(dataset_detail_query_model)
    #@api.marshal_with(ds_model)
    def post(self):
        '''Get single dataset object'''
        req_obj = request.json
        
        ver_list = get_ver_list(req_obj["bcoid"])
        
        req_obj["coll"] = "c_extract"
        extract_obj = get_one(req_obj)
        if "error" in extract_obj:
            return extract_obj
       
        res = get_many_text_search({"coll":"c_records", "query":req_obj["bcoid"]})

        row_list_one, row_list_two = [], []
        limit_one, limit_two = 1000, 1000
        row_count_one, row_count_two = 0, 0
        req_obj["rowlist"] = [] if "rowlist" not in req_obj else req_obj["rowlist"]

        for obj in res["recordlist"]:
            row_idx = int(obj["recordid"].split("_")[-1])
            row = json.loads(obj["row"])
            if row_idx in  req_obj["rowlist"] and row_count_one < limit_one:
                row_list_one.append(row)
                row_count_one += 1
            elif row_count_two < limit_two:
                row_list_two.append(row)
                row_count_two += 1
            if row_count_one > limit_one and row_count_two > limit_two:
                break



        if extract_obj["record"]["sampledata"]["type"] == "table":
            header_row = []
            for obj in extract_obj["record"]["sampledata"]["data"][0]:
                header_row.append(obj["label"])
            extract_obj["record"]["alldata"] = {"type":"table", "data":[]}
            extract_obj["record"]["resultdata"] = {"type":"table", "data":[]}
            extract_obj["record"]["resultdata"]["data"].append(header_row)
            extract_obj["record"]["alldata"]["data"].append(header_row)
            extract_obj["record"]["resultdata"]["data"] += row_list_one
            extract_obj["record"]["alldata"]["data"] += row_list_two
        elif extract_obj["record"]["filetype"] in ["gz"]:
            extract_obj["record"]["alldata"] = {"type":"html", "data":"<pre>"}
            extract_obj["record"]["resultdata"] = {"type":"html", "data":"<pre>"}
            r_list_one, r_list_two = [], []
            for row in row_list_one:
                r_list_one.append("\n"+row[0])
            for row in row_list_two:
                r_list_two.append("\n"+row[0])
            extract_obj["record"]["resultdata"]["data"] = "\n".join(r_list_one)
            extract_obj["record"]["alldata"]["data"] = "\n".join(r_list_two)
        elif extract_obj["record"]["sampledata"]["type"] in ["html"]:
            extract_obj["record"]["alldata"] = {"type":"html", "data":"<pre>"}
            extract_obj["record"]["resultdata"] = {"type":"html", "data":"<pre>"}
            r_list_one, r_list_two = [], []
            for row in row_list_one:
                r_list_one.append("\n>"+row[-1]+"\n"+row[0])
            for row in row_list_two:
                r_list_two.append("\n>"+row[-1]+"\n"+row[0])
            extract_obj["record"]["resultdata"]["data"] = "\n".join(r_list_one)
            extract_obj["record"]["alldata"]["data"] = "\n".join(r_list_two)
        elif extract_obj["record"]["sampledata"]["type"] in ["text"]:
            extract_obj["record"]["alldata"] = {"type":"html", "data":"<pre>"}
            extract_obj["record"]["resultdata"] = {"type":"html", "data":"<pre>"}
            r_list_one, r_list_two = [], []
            for row in row_list_one:
                r_list_one.append(row[0])
            for row in row_list_two:
                r_list_two.append(row[0])
            extract_obj["record"]["resultdata"]["data"] = "\n".join(r_list_one)
            extract_obj["record"]["alldata"]["data"] = "\n".join(r_list_two)

        extract_obj["record"].pop("sampledata")


        req_obj["coll"] = "c_history"
        req_obj["doctype"] = "track"
        history_obj = get_one(req_obj)
        if "error" in history_obj:
            return history_obj

        
        history_dict = {}
        for ver in history_obj["record"]["history"]:
            if ver in ver_list:
                history_dict[ver] = history_obj["record"]["history"][ver]


        req_obj["coll"] = "c_bco"
        req_obj["bcoid"] = "https://biocomputeobject.org/%s" % (req_obj["bcoid"])
        bco_obj = get_one(req_obj)
        if "error" in bco_obj:
            return bco_obj

        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        #return list(bco_obj["record"].keys())
        bco_obj["record"] = order_json_obj(bco_obj["record"], config_obj["bco_field_order"])
        #return list(bco_obj["record"].keys())
        res_obj = {
            "status":1,
            "record":{
                "extract":extract_obj["record"], 
                "bco":bco_obj["record"], 
                "history":history_dict
            }
        }

        return res_obj


@api.route('/pagecn')
class Dataset(Resource):
    '''Get static page content '''
    @api.doc('get_dataset')
    @api.expect(pagecn_query_model)
    #@api.marshal_with(ds_model)
    def post(self):
        '''Get static page content '''
        req_obj = request.json
        req_obj["coll"] = "c_html"
        res_obj = get_one(req_obj)
        return res_obj


@api.route('/historylist')
class HistoryList(Resource):
    '''Get dataset history list '''
    @api.doc('historylist')
    @api.expect(dataset_historylist_query_model)
    #@api.marshal_list_with(ds_model)
    def post(self):
        '''Get dataset history list '''
        req_obj = request.json
        req_obj["coll"] = "c_history"
        req_obj["query"] = "" if "query" not in req_obj else req_obj["query"]

        hist_obj = get_many(req_obj)
        if "error" in hist_obj:
            return hist_obj
        res_obj = {"tabledata":{"type": "table","data": []}}
        header_row = [
            {"type": "string", "label": "BCOID"}
            ,{"type": "string", "label": "File Name"}
            ,{"type": "number", "label": "Field Count"}
            ,{"type": "number", "label": "Fields Added"}
            ,{"type": "number", "label": "Fields Removed"}
            ,{"type": "number", "label": "Row Count"}
            ,{"type": "number", "label": "Rows Count Prev"}
            ,{"type": "number", "label": "Rows Count Change"}
            ,{"type": "number", "label": "ID Count"}
            ,{"type": "number", "label": "IDs Added"}
            ,{"type": "number", "label": "IDs Removed"}
            ,{"type": "string", "label": ""}

        ]
        f_list = ["file_name", 
            "field_count", "fields_added", "fields_removed", 
            "row_count", "row_count_last", "row_count_change",
            "id_count", "ids_added", "ids_removed"
        ]
        res_obj["tabledata"]["data"].append(header_row)
        for obj in hist_obj["recordlist"]:
            if "history" in obj:
                ver_one = req_obj["dataversion"]
                ver_two = ver_one.replace(".", "_")
                if ver_two in obj["history"]:
                    row = [obj["bcoid"]]
                    for f in f_list:
                        row.append(obj["history"][ver_two][f])
                    row.append("<a href=\"/%s/%s/history\">details</a>" % (obj["bcoid"],ver_one))
                    match_flag = True
                    idx_list = []
                    if req_obj["query"] != "":
                        q = req_obj["query"].lower()
                        for v in [row[0].lower(), row[1].lower()]:
                            idx_list.append(v.find(q))
                        match_flag = False if idx_list == [-1,-1] else match_flag

                    if match_flag == True:
                        res_obj["tabledata"]["data"].append(row)


        return res_obj


@api.route('/historydetail')
class HistoryDetail(Resource):
    '''Show a single dataset history object'''
    @api.doc('get_dataset')
    @api.expect(dataset_historydetail_query_model)
    #@api.marshal_with(ds_model)
    def post(self):
        '''Get single dataset history object'''
        req_obj = request.json
        req_obj["coll"] = "c_history"
        res_obj = get_one(req_obj)
        if "error" in res_obj:
            return res_obj

        res_obj["record"]["history"] = res_obj["record"]["history"][req_obj["dataversion"].replace(".","_")]
        return res_obj



@api.route('/init')
class Dataset(Resource):
    '''Get init '''
    @api.doc('get_dataset')
    @api.expect(init_query_model)
    def post(self):
        '''Get init '''
        #req_obj = request.json
        req_obj = {}
        req_obj["coll"] = "c_init"
        res_obj = get_one(req_obj)
        return res_obj



@api.route('/upload', methods=['GET', 'POST'])
class DatasetUpload(Resource):
    '''Upload dataset item'''
    @api.doc('upload_dataset')
    @api.expect(dataset_upload_query_model)
    #@api.marshal_with(ds_model)
    def post(self):
        '''Upload dataset'''
        res_obj = {}
        req_obj = request.form
        error_obj = {}
        if request.method != 'POST':
            error_obj = {"error":"only POST requests are accepted"}
        elif 'userfile' not in request.files and 'file' not in request.files:
            error_obj = {"error":"no file parameter given"}
        else:
            file = request.files['userfile'] if "userfile" in request.files else request.files['file']
            file_format = req_obj["format"]
            qc_type = req_obj["qctype"]
            data_version = req_obj["dataversion"]
            file_data = []
            if file.filename == '':
                error_obj = {"error":"no filename given"}
            else:
                file_name = secure_filename(file.filename)
                data_path, ser = os.environ["DATA_PATH"], os.environ["SERVER"]
                out_file = "%s/userdata/%s/tmp/%s" % (data_path, ser, file_name)
                file.save(out_file)
                res_obj = {
                    "inputinfo":{"name":file_name, "format":file_format}, 
                    "summary":{"fatal_qc_flags":0, "total_qc_flags":0},
                    "failedrows":[]
                }

                error_obj = run_qc(out_file, file_format, res_obj, qc_type, data_version)
        res_obj = error_obj if error_obj != {} else res_obj
        return res_obj


@api.route('/submit')
class Dataset(Resource):
    '''Submit dataset '''
    @api.doc('get_dataset')
    @api.expect(dataset_submit_query_model)
    def post(self):
        '''Submit dataset '''
        req_obj = request.json
        data_path, ser = os.environ["DATA_PATH"], os.environ["SERVER"]
        src_file = "%s/userdata/%s/tmp/%s" % (data_path, ser, req_obj["filename"])
        dst_dir = "%s/userdata/%s/%s" % (data_path, ser, req_obj["affilation"])
        if os.path.isfile(src_file) == False:
            res_obj = {"error":"submitted filename does not exist!", "status":0}
        else:
            if os.path.isdir(dst_dir) == False:
                dst_dir = "%s/userdata/%s/%s" % (data_path, ser, "other")
            today = datetime.datetime.today()
            yy, mm, dd = today.year, today.month, today.day
            dst_file = "%s/%s_%s_%s_%s" % (dst_dir, mm, dd, yy, req_obj["filename"])
            json_file = ".".join(dst_file.split(".")[:-1]) + ".json"

            cmd = "cp %s %s" % (src_file, dst_file)
            x, y = subprocess.getstatusoutput(cmd)
            if os.path.isfile(dst_file) == False:
                res_obj = {"error":"save file failed!", "status":0}
            else:
                res_obj = {"confirmation":"Dataset file has been submitted successfully!", "status":1}
                with open(json_file, "w") as FW:
                    FW.write("%s\n" % (json.dumps(req_obj, indent=4)))
        return res_obj



@api.route('/glycan_finder')
class Dataset(Resource):
    '''Glycan Finder '''
    @api.doc('get_dataset')
    @api.expect(glycan_finder_query_model)
    def post(self):
        '''Glyca Finder '''
        req_obj = request.json
        data_path, ser = os.environ["DATA_PATH"], os.environ["SERVER"]
        uploaded_file = "%s/userdata/%s/tmp/%s" % (data_path, ser, req_obj["filename"])
        
        output_file = "%s/userdata/%s/tmp/%s_output_%s.txt" % (data_path, ser, req_obj["filename"], os.getpid())

        if os.path.isfile(uploaded_file) == False:
            res_obj = {"error":"submitted filename does not exist!", "status":0}
        else:
            file_format = req_obj["filename"].split(".")[-1]
            cmd = "sh /hostpipe/glycan_finder.sh %s %s" % (uploaded_file, output_file)
            glycan_list = []
            if ser != "dev":
                glycan_list = subprocess.getoutput(cmd).strip().split(",")
            else:
                glycan_list = ["A", "B"]
                time.sleep(5)

            res_obj = {
                "inputinfo":{"name":req_obj["filename"], "format":file_format},
                "mappingrows":[
                    [
                        {"type": "string", "label": "GlyToucan Accession"},
                        {"type": "string", "label": "Glycan Image"}
                    ]
                ]
            }
            for ac in glycan_list:
                link_one = "<a href=\"https://glygen.org/glycan/%s\" target=_>%s</a>" % (ac,ac)
                link_two = "<a href=\"https://gnome.glyomics.org/restrictions/GlyGen.StructureBrowser.html?focus=%s\" target=_>related glycans</a>" % (ac)
                img = "<img src=\"https://api.glygen.org/glycan/image/%s\">" % (ac)
                links = "%s (other %s)" % (link_one, link_two)
                res_obj["mappingrows"].append([links, img])

        return res_obj





@api.route('/download/')
class Data(Resource):
    @api.expect(download_query_model)
    def post(self):
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "conf/config.json")
        config_obj = json.load(open(json_url))
        res_obj = {}
        req_obj = request.json
        req_obj["coll"] = "c_extract"
        extract_obj = get_one(req_obj)
        if "error" in extract_obj:
            return extract_obj
        header_row = []
        for obj in extract_obj["record"]["sampledata"]["data"][0]:
            header_row.append(obj["label"])

        res = get_many_text_search({"coll":"c_records", "query":req_obj["bcoid"]})
        if "error" in res:
            return res
        row_list = [header_row]
        for obj in res["recordlist"]:
            row_idx = int(obj["recordid"].split("_")[-1])
            row = json.loads(obj["row"])
            if row_idx in  req_obj["rowlist"]:
                row_list.append(row)
        res_obj = {"status":1, "rowlist":row_list}
        
        return res_obj

    @api.doc(False)
    def get(self):
        return self.post()


