---------------
  Front end:
---------------

1.Send Product price with input field named as 'price'

2.Send Product quantity with input field named as 'qty'

3.action url must be at  SendPerformREQuest.php

----------------
  Backend:
----------------

1.include SendPerformREQuest.php and GetHandlerResponse.php on server

2.change Tran portal Id,Tran portal Password,Terminal Resource Key,ReqUdf1,ReqUdf2,ReqUdf3,ReqUdf4,ReqUdf5 if required 
on SendPerformREQuest.php

3.rename localhost on SendPerformREQuest.php line number at 86 to your site address

4.rename localhost on SendPerformREQuest.php line number at 96 to  your site address

5. change ErrorUrl to your site address and set error page name

6.change  header address on GetHandlerResponse.php at line 48 to your site result page

7.change  header address on GetHandlerResponse.php at line 53 to your site error page
