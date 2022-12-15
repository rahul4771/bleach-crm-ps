<?php

define ('HMAC_SHA256', 'sha256');
//live secret key
define ('SECRET_KEY', '5bf07594d80c4f13b271164c42e982b3cb7d51654deb4adf87f2d5c6fc9fe8a2fa52fdcc5a854d1a9c48f2893c852bef27e3e148376641e68af6e867cf2ef982b579887e405b4b83a8ac4c77ab603d08744543bc80714e13a040ad7c8a8285d8ff63f717c01747b1ad699f3e757bff429a979ea4f77d4386a605c01bc0f727f3');

//test secret key
//define ('SECRET_KEY', '06bac58a11844f92862e822331935ec716a62a6187e24ce8ab3bbb6f1d02761b492700faec154bb99834769b55b9629452252b2b484d40e586261fceb310d74e7ec22417b9ec42778174725e247b53b7633990133451446887d82858ef05a396680751e2ca2e4d27a168b9892bfe41cccd3e762f8ad34c27891932fc8bf6283d');

function sign ($params) {
  return signData(buildDataToSign($params), SECRET_KEY);
}

function signData($data, $secretKey) {
    return base64_encode(hash_hmac('sha256', $data, $secretKey, true));
}

function buildDataToSign($params) {
        $signedFieldNames = explode(",",$params["signed_field_names"]);
        foreach ($signedFieldNames as $field) {
           $dataToSign[] = $field . "=" . $params[$field];
        }
        return commaSeparate($dataToSign);
}

function commaSeparate ($dataToSign) {
    return implode(",",$dataToSign);
}

?>
