<?php

define ('HMAC_SHA256', 'sha256');
define ('SECRET_KEY', '5bf07594d80c4f13b271164c42e982b3cb7d51654deb4adf87f2d5c6fc9fe8a2fa52fdcc5a854d1a9c48f2893c852bef27e3e148376641e68af6e867cf2ef982b579887e405b4b83a8ac4c77ab603d08744543bc80714e13a040ad7c8a8285d8ff63f717c01747b1ad699f3e757bff429a979ea4f77d4386a605c01bc0f727f3');

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
