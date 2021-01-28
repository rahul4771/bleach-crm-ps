<?php

define ('HMAC_SHA256', 'sha256');
define ('SECRET_KEY', '7c35e655d7fc4b4f93066f44c07bd95bafadce5898824c1c8cce364187267efa77937064107f4659b708a1d39c8efe5b2174717a49304e50a14254fde3250929f8c13c7f182640a5ab64d9fe1d3239ce74e75e7e2d3a423cb41f47659ab89296a84a45cdcaeb436788c48e4a6a9e53604858832d5843446fbef1d2d8e1fdf715');

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
