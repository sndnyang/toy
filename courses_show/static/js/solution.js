
function getRequest() {   
   var url = location.search; //获取url中"?"符后的字串   
   var theRequest = new Object();   
   if (url.indexOf("?") != -1) {   
      var str = url.substr(1);   
      strs = str.split("&");   
      for(var i = 0; i < strs.length; i ++) {   
         theRequest[strs[i].split("=")[0]] = decodeURI(strs[i].split("=")[1]);
      }   
   }
   else {
       return null;
   }
   return theRequest;   
}


function getSolution() {

   var url = location.search; //获取url中"?"符后的字串   
   if (url.indexOf("?") === -1) {   
       return;
   }
  //var params = getRequest();
  //if (!params) {
  //    return;
  //}
    $.get({
        url: '/getsolution?'+url.split('?')[1],
        dataType: 'json',
    //data: JSON.stringify(params),
        success: function (data) {
            console.log(data);
            var code = data.code;
            if (!code) {
                alert(data.info)
                return;
            }

            showSolution(data);
        }
    });


}
