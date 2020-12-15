<html>
<head>
    <title>Secure Acceptance - Payment Form Example</title>
    <link rel="stylesheet" type="text/css" href="payment.css"/>
    <script type="text/javascript" src="jquery-1.7.min.js"></script>
</head>
<body>
<form id="payment_form" action="http://payment.bleachkw.com:8085/creditcard/payment_confirmation.php" method="post">
    <input type="hidden" name="access_key" value="dc9b55c60e193d98a5861569b4c40d6b">
    <input type="hidden" name="profile_id" value="340591FC-E863-4714-81A5-FFC0D7B5D9A7">
    <input type="hidden" name="transaction_uuid" value="<?php echo uniqid() ?>">
    <input type="hidden" name="signed_field_names" value="access_key,profile_id,transaction_uuid,signed_field_names,unsigned_field_names,signed_date_time,locale,transaction_type,reference_number,amount,currency,bill_to_forename,bill_to_surname,bill_to_email,bill_to_phone,bill_to_address_country,bill_to_address_city,bill_to_address_line1,merchant_defined_data1,merchant_defined_data2,merchant_defined_data4,merchant_defined_data5,merchant_defined_data7,merchant_defined_data20,customer_ip_address">
    <input type="hidden" name="unsigned_field_names">
    <input type="hidden" name="signed_date_time" value="<?php echo gmdate("Y-m-d\TH:i:s\Z"); ?>">
    <input type="hidden" name="locale" value="en">
    <fieldset>
        <legend>Payment Details</legend>
        <div id="paymentDetailsSection" class="section">
            <span>transaction_type:</span><input type="text" name="transaction_type" size="25" value="<?php echo htmlspecialchars($_GET['transaction_type']);?>" readonly><br/>
            <span>reference_number:</span><input type="text" name="reference_number" size="25" value="<?php echo htmlspecialchars($_GET['reference_number']);?>" readonly><br/>
            <span>amount:</span><input type="text" name="amount" size="25" value="<?php echo htmlspecialchars($_GET['amount']);?>" readonly><br/>
            <span>currency:</span><input type="text" name="currency" size="25" value="<?php echo htmlspecialchars($_GET['currency']);?>" readonly><br/>
        
            <input type="hidden" name="bill_to_forename" value="<?php echo htmlspecialchars($_GET['bill_to_forename']);?>">
            <input type="hidden" name="bill_to_surname" value="<?php echo htmlspecialchars($_GET['bill_to_surname']);?>">
            <input type="hidden" name="bill_to_phone" value="<?php echo htmlspecialchars($_GET['bill_to_phone']);?>">
            <input type="hidden" name="bill_to_email" value="<?php echo htmlspecialchars($_GET['bill_to_email']);?>">
            <input type="hidden" name="bill_to_address_country" value="<?php echo htmlspecialchars($_GET['bill_to_address_country']);?>">
            <input type="hidden" name="bill_to_address_city" value="<?php echo htmlspecialchars($_GET['bill_to_address_city']);?>">
            <input type="hidden" name="bill_to_address_line1" value="<?php echo htmlspecialchars($_GET['bill_to_address_line1']);?>">
            <input type="hidden" name="merchant_defined_data1" value="<?php echo htmlspecialchars($_GET['merchant_defined_data1']);?>">
            <input type="hidden" name="merchant_defined_data2" value="<?php echo htmlspecialchars($_GET['merchant_defined_data2']);?>">
            <input type="hidden" name="merchant_defined_data4" value="<?php echo htmlspecialchars($_GET['merchant_defined_data4']);?>">
            <input type="hidden" name="merchant_defined_data5" value="<?php echo htmlspecialchars($_GET['merchant_defined_data5']);?>">
            <input type="hidden" name="merchant_defined_data7" value="<?php echo htmlspecialchars($_GET['merchant_defined_data7']);?>">
            <input type="hidden" name="merchant_defined_data20" value="<?php echo htmlspecialchars($_GET['merchant_defined_data20']);?>">
            <input type="hidden" name="customer_ip_address" value="<?php echo htmlspecialchars($_GET['customer_ip_address']);?>">
        </div>
    </fieldset>
    <input type="submit" id="submitbtn" name="submitbtn" value="Submit"/>
    <script type="text/javascript" src="payment_form.js"></script>
</form>
</body>
</html>

<script type="text/javascript">
//    document.getElementById('payment_form').submit(); // SUBMIT FORM
</script>

