<?php

define ('HMAC_SHA256', 'sha256');
//live secret key
define ('SECRET_KEY', '144d7a1975504a38b3b2bbc5f35861bc380d1b89c38d457daa5bcae83c2bf7e391bce09ba73f45ae945ec737bb494034bf39e547e3d84fd09748d151ac06dccf8d94fbe9cb9b43b4af9185a133ad4567d0762933157b41ff890c152b85d310913fbe8679dbd04f0f839e6d90c2797e5a674c3846fe81438a89db05640f4df908');

//test secret key
// define ('SECRET_KEY', '06bac58a11844f92862e822331935ec716a62a6187e24ce8ab3bbb6f1d02761b492700faec154bb99834769b55b9629452252b2b484d40e586261fceb310d74e7ec22417b9ec42778174725e247b53b7633990133451446887d82858ef05a396680751e2ca2e4d27a168b9892bfe41cccd3e762f8ad34c27891932fc8bf6283d');

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
