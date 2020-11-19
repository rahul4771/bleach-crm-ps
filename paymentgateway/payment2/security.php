<?php

define ('HMAC_SHA256', 'sha256');
define ('SECRET_KEY', 'f8c2f4b1ce0643f9a31d30337802f9984f70871bf50e464d9f9fe00c70c424cba68ddd9354cd4cee82ea19d74fc221171c0f9604c05f4abf942f34f9b1a4cea94540552844b4425789a5253ece0fe1ba9fe35dc2612f45b5bf1130d02c80eecc5faec661fad34e18be6ef760707b8aaed56bdbb3044e4cb7997227d42975e3ce');

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
