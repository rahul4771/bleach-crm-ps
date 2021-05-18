
//$('#cl-evaluator-1').height($('#slot-row-1').height());

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();  
   
  });

  function openModal(){
   
   
  }
  function selectSlot(elem){
    console.log("elem is "+elem)
    $(elem).toggleClass('time-slot-active')
  }


  /** vue js */


  new Vue({

    el: '#app',
    vuetify: new Vuetify(),
    delimiters: ['<%', '%>'],
   
    
    data: {
        agent:'#0D87C5',
        selectedDate:new Date().toISOString().substr(0, 10),
        selectedEvaluator:'Ahamed Abdou',
        lateHour:false,
        editEval:false
      }
  })

