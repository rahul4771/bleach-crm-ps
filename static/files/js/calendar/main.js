
//$('#cl-evaluator-1').height($('#slot-row-1').height());

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();  
    $('#cleaningCalendar-carousel').owlCarousel({
        loop:false,
        margin:10,
        nav:false,
        responsive:{
            0:{
                items:1
            },
            600:{
                items:3
            },
            1000:{
                items:5
            }
        }
    })
   
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
        cleaningDate:new Date().toISOString().substr(0, 10),
        selectedDate:new Date().toISOString().substr(0, 10),
        selectedEvaluator:'Ahamed Abdou',
        lateHour:false,
        editEval:false,
        delAlert:false,
        customer:'#139275',
        cancelled:'#8B8B8B',
        primary:'#2d4e85',
        selectedCleaningSlot:[],
        services:[],
        slots:{},
        combineSlots:[],
        url:'https://test.bleach-kw.com'
      },
      mounted(){
        this.getSlots()
        this.parseDate()
      },
      methods:{
          parseDate(){
            this.cleaningDate=this.selectedDate.split('-')[2]+'-'+this.selectedDate.split('-')[1]+'-'+this.selectedDate.split('-')[0]
          },
          getSlots(){
            axios.get(this.url+"/agent/cleaningcallendar?cleaning_callendar_date=31-07-2021").then((response) => {
                this.slots = response.data;
                for(var i=0;i<this.slots.notapproved_cleanings.length;i++){
                   
                    this.combineSlots.push({type:'not approved',slots:this.slots.notapproved_cleanings[i]})
                }
                for(var j=0;j<this.slots.appoved_cleanings.length;j++){
                   
                    this.combineSlots.push({type:'approved',slots:this.slots.appoved_cleanings[j]})
                }
                for(var k=0;k<this.slots.followup_cleanings.length;k++){
                   
                    this.combineSlots.push({type:'followup',slots:this.slots.followup_cleanings[k]})
                }
              })
          },
          startChecker(start,end,hour){
              start=start.split(':')[0]
              end=end.split(':')[0]
            if(start[0]=='0'){
                start=start[1]
            }
            if(end[0]=='0'){
                end=end[1]
            }
            var begin=parseInt(start)
            var stop=begin+hour
            if(stop>12){
                stop=stop-12
            }
            console.log("stop :"+stop)
            console.log("end :"+end)
            if(stop==end){

                return true
            }

            
          },
          checkAll(slot_start,slot_end,start_at,end_at,cleaning_hours){
            this.cleaningDate='31-07-2021'
              var endTime=end_at.split(' ')[1]
              var endDate=end_at.split(' ')[0]
              
              var endUnit=end_at.split(' ')[2]
              var startTime=start_at.split(' ')[1]
              var startDate=start_at.split(' ')[0]
              var startUnit=start_at.split(' ')[2]
              var slotStart=slot_start.split(' ')[0]
              var slotStartUnit=slot_start.split(' ')[1]
              var slotEnd=slot_end.split(' ')[0]
              var slotEndUnit=slot_end.split(' ')[1]
              if(cleaning_hours==3){
                  if(startTime==slotStart && slotStartUnit==startUnit && slotEndUnit==endUnit){
                      return 'start-end'
                  }
              }

              else if(cleaning_hours>3){
                if(startTime==slotStart && endTime!=slotEnd && slotStartUnit==startUnit){
                    return 'start-only'
                }
                else if(startTime!=slotStart && endTime==slotEnd && slotEndUnit==endUnit && this.cleaningDate==endDate){
                 
                    return 'end-only'
                   
                   
                    
                }
                else {
                    

                        var slotStartVal=parseInt(slotStart.split(':')[0])
                        var slotEndVal=parseInt(slotEnd.split(':')[0])
                        var startVal=parseInt(startTime.split(':')[0])
                        var endVal=parseInt(endTime.split(':')[0])
                        if(startDate==endDate){
                        if(startUnit=='PM'){
                            startVal=startVal+12
                        }
                        if(endUnit=='PM'){
                            endVal=endVal+12
                        }
                        if(slotStartUnit=='PM'){
                            slotStartVal=slotStartVal+12
                        }
                        if(slotEndUnit=='PM'){
                            slotEndVal=slotEndVal+12
                        }
                            if(slotStartVal<endVal && slotStartVal>startVal){
                                return 'continue'
                            }
                        }
                        else{
                            if(startUnit=='PM'){
                                startVal=startVal+12
                            }
                            if(endUnit=='PM'){
                                endVal=endVal+12
                            }
                            if(slotStartUnit=='PM'){
                                slotStartVal=slotStartVal+12
                            }
                            if(slotEndUnit=='PM'){
                                slotEndVal=slotEndVal+12
                            }
                            if(slotStartVal>startVal && slotStartVal!=24){
                                return 'continue'
                            }
                        }

                        

                    
                   
                    
                }

              }



          },
          changeCleaningDate(){
            console.log("new date "+ $('#cl_cleaning_calendar').val())

          }
      }
  })

 
  //New Date picker
  $('.next-day').on('click', function () {

    $selectedDay            = $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").getDate();
    var $tmpSelectedDay     = new Date($selectedDay) 
    $tmpSelectedDay.setDate($tmpSelectedDay.getDate() + 1);
    $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
        
 });


$('.prev-day').on('click', function () {

    $selectedDay            = $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").getDate();
    var $tmpSelectedDay     = new Date($selectedDay) 
    $tmpSelectedDay.setDate($tmpSelectedDay.getDate() - 1);
    $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));

});

$('.today-date').on('click', function () {
    var $tmpSelectedDay     = new Date();
    $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
});


