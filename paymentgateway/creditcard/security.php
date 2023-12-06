<?php

define ('HMAC_SHA256', 'sha256');
//live secret key
// define ('SECRET_KEY', 'c7bd5680eb9e403db1f64d7997cb474d2495fda1e52c42f3bcd3bf02396d9687d09d6c2f321149c2832110fef2a456ebfaa71cdb02b44b808771ca9d80508bfaf805b8038bcc49aeaf22edb8b98b36ccf1e0436ac4f849eb94d58c19b6489add41ba739239464e478a694c4cb803d710261e45a2ede74a208d6648b16e4f2af7');

//test secret key
define ('SECRET_KEY', '06bac58a11844f92862e822331935ec716a62a6187e24ce8ab3bbb6f1d02761b492700faec154bb99834769b55b9629452252b2b484d40e586261fceb310d74e7ec22417b9ec42778174725e247b53b7633990133451446887d82858ef05a396680751e2ca2e4d27a168b9892bfe41cccd3e762f8ad34c27891932fc8bf6283d');

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
