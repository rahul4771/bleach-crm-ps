
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


const app=  new Vue({

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
        slotDate:'',
        dateSelected:'',
        evaluators:[],
        booking:{
            booking_date:'',
            booking_time:''
        },
        convertedTime:{
            earlyHours:[],
            lateHours:[]
          },
         
          lateHours:false,
        selectedTime:'',
        timeSlots:[],
        url:'https://test.bleach-kw.com'
      },
      mounted(){
        this.getSlots()
        this.parseDate()
        
        //moment.tz.setDefault("Asia/Baghdad");
        console.log("current time is" + moment().format());
    
        this.dateSelected = moment().format().split("T")[0];
        this.today = moment().format().split("T")[0];
        this.formatDate()
        this.getEvaluationSlots()
      },
      methods:{
          setEvaluators(evaluatorList){
            this.evaluators=evaluatorList
          },
        getTime(){
            if(!this.lateHours)
            {
            return this.convertedTime.earlyHours
            }
            else{
              //return this.convertedTime.earlyHours.concat(this.convertedTime.lateHours)
              return this.timeSlots
            }
          },
          convertTime(){
            this.convertedTime.earlyHours=[],
            this.convertedTime.lateHours=[]
            for(var i=8;i<24;i++){
              if(this.timeSlots.includes(i)){
                if(i<20)
                {
                this.convertedTime.earlyHours.push(i)
                }
                else{
                  this.convertedTime.lateHours.push(i)
                }
              }
            }
            for(var i=0;i<8;i++){
              if(this.timeSlots.includes(i)){
                this.convertedTime.lateHours.push(i)
              }
            }
    
    
          },
          selectTime(time,slot){
            this.booking.booking_time=time
            this.selectedTime=slot
          },
        formatDate() {
            var slotDate = this.dateSelected;
            var slotYear = slotDate.split("-")[0];
            var slotMonth = slotDate.split("-")[1];
            var slotDay = slotDate.split("-")[2];
            if (slotDay[0] == 0) {
              slotDay = slotDay[1];
            }
            if (slotMonth[0] == 0) {
              slotMonth = slotMonth[1];
            }
            this.slotDate = slotDay + "-" + slotMonth + "-" + slotYear;
            
          },
          getEvaluationSlots(){
            this.formatDate()
            this.booking.booking_date=this.slotDate
            this.booking.booking_time=''
            this.selectedTime=''
            axios
              .get(
                 this.url+"/customer/ajax/evaluationslotes?evaluation_booking_date="+this.slotDate
               
              )
              .then((response) => {
                 this.timeSlots = response.data.slotes;
                 this.convertTime()
                 if(response.data['ERROR']){
                   this.errMsg=response.data['ERROR']
                 }
               
      
                //this.parseSize();
              })
               .catch((error) => {
                console.log(error);
              });
          },
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
                    var slot=this.slots.followup_cleanings[k]
                    //this.slots.followup_cleanings[k]['cleaning_hours']=this.slots.followup_cleanings[k].follow_up.cleaning_hours
                    slot.cleaning_hours=slot.follow_up.cleaning_hours
                    slot.order={order_no:slot.follow_up.ticket_no}
                    this.combineSlots.push({type:'followup',slots:slot})
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


