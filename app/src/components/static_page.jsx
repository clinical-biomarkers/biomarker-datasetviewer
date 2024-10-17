import React, { Component } from "react";
import Alertdialog from './dialogbox';
import Loadingicon from "./loading_icon";
import * as LocalConfig from "./local_config";
import { Link } from "react-router-dom";
import DoubleArrowOutlinedIcon from '@material-ui/icons/DoubleArrowOutlined';
import { Markup } from 'interweave';

import $ from "jquery";


class StaticPage extends Component {
  
  state = {
    tabidx:"sampleview",
    dialog:{
      status:false, 
      msg:""
    }
  };

  

  handleDialogClose = () => {
    var tmpState = this.state;
    tmpState.dialog.status = false;
    this.setState(tmpState);
  }

  componentDidMount() {

    $(document).on('click', '.faqquestion', function (event) {
        event.preventDefault();
        var jqId = "#answer_" + this.id.split("_")[1];
        $(jqId).toggle();
    });

    var reqObj = {pageid:this.props.pageId};
    const requestOptions = { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqObj)
    };
    const svcUrl = LocalConfig.apiHash.dataset_static_content;

    fetch(svcUrl, requestOptions)
      .then((res) => res.json())
      .then(
        (result) => {
          var tmpState = this.state;
          tmpState.response = result;
          tmpState.isLoaded = true;          
          if (tmpState.response.status == 0){
            tmpState.dialog.status = true;
            tmpState.dialog.msg = tmpState.response.error;
          }
          console.log("Request:",svcUrl);
          console.log("AAAA", result);
          this.setState(tmpState);
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error,
          });
        }
      );
  }


  handleTitleClick = (e) => {

    var tmpState = this.state;
    tmpState.tabidx = e.target.id.split("-")[0];
    this.setState(tmpState);
  };



  render() {

    if (!("response" in this.state)){
      return <Loadingicon/>
    }
    var pageIdLabel = this.props.pageId.toUpperCase();
    var pageCn = ( this.state.dialog.status === true ? "no content found" : this.state.response.record.cn);

    return (
      <div className="pagecn">
        <Alertdialog dialog={this.state.dialog} onClose={this.handleDialogClose}/>
        <div className="leftblock" style={{width:"100%", 
          margin:"60px 0px 0px 0px", 
          fontSize:"17px", borderBottom:"1px solid #ccc"}}>
          <DoubleArrowOutlinedIcon style={{color:"#2358C2", fontSize:"17px" }}/>
          &nbsp;
          <Link to="/" className="reglink">HOME </Link> 
            &nbsp; / &nbsp;
          <Link to={"/static/"+this.props.pageId} className="reglink">{pageIdLabel}</Link> 
        </div>

        <div className="leftblock" style={{width:"100%", margin:"40px 0px 0px 0px"}}>
          <Markup content={pageCn}/>
        </div>


      </div>
    );
  }
}

export default StaticPage;
