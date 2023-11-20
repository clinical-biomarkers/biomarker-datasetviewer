prj="biomarkerdb"
# srv="prd"
#srv="beta"
srv="tst"


sudo systemctl stop docker-$prj-api-$srv.service
python3 create_api_container.py -s $srv
sudo systemctl start docker-$prj-api-$srv.service


