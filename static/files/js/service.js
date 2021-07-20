//Service file
//using async funcation to call service methods


var api='https://my.bleachkw.com/';

async function _post(url,data){
    let result;
    await axios.post(api+url , data).then(response => {
        result = response;
      })
      .catch(({ response }) => {
        result = response;
      });
    return result;
}

async function _get(url){
    let result;
    await axios.get(api+url).then(response => {
        result = response;
      })
      .catch(({ response }) => {
        result = response;
      });
    return result;
}