//Service file
//use async funcation to call service methods
//Check Response status always

// var api ='https://my.bleachkw.com';
 //var url ='https://my.bleachkw.com';

//var api ='https://test.bleach-kw.com';
//var url ='https://test.bleach-kw.com';

// var api ='http://127.0.0.1:8000';
// var url ='http://127.0.0.1:8000';

//var api='https://test.bleach-kw.com';
var api = 'http://localhost:8000'
var api = 'http://localhost:8000'


async function _post(url,data){
    let result;
    await axios.post(api+'/'+url , data).then(response => {
        result = response;
      })
      .catch(({ response }) => {
        result = response;
      });
    return result;
}

async function _get(url){
  console.log(url)
    let result;
    await axios.get(api+'/'+url).then(response => {
        result = response;
      })
      .catch(({ response }) => {
        result = response;
      });
    return result;
}

async function _put(url,data){
  let result;
  await axios.put(api+'/'+url , data).then(response => {
      result = response;
    })
    .catch(({ response }) => {
      result = response;
    });
  return result;
}