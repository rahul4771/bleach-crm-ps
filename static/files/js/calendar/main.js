
//$('#cl-evaluator-1').height($('#slot-row-1').height());

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
    $( ".scroll-cal" ).scrollLeft( 650 ); 
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
        setAttenderNotes:"",
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
        selectedSlot:'1',
        evaluators:[],
        currentTime:'',
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
        today:'',
        timeSlots:[],
        parsedSlots:[],
        slot:{
          "1":{
            slots:[]
          },
          "2":{
            slots:[]
          },
          "3":{
            slots:[]
          },
          "4":{
            slots:[]
          },
          "5":{
            slots:[]
          },
          "6":{
            slots:[]
          },
          "7":{
            slots:[]
          },
          "8":{
            slots:[]
          },
        },
        url:'https://test.bleach-kw.com'
      },
      mounted(){
        this.getSlots()
        this.parseDate()
        moment.locale('fr');
        this.currentTime=moment().format().split("T")[1];
        this.dateSelected = moment().format().split("T")[0];
        this.today = moment().format().split("T")[0];
       
       
        console.log("today is "+this.today)
        console.log("time is "+this.currentTime)
        //console.log("tiime is "+moment().format("hh:mm A"))
       // moment(currentTime).format("hh:mm"))

        this.formatDate()
        this.getEvaluationSlots()
      },
      methods:{
        closeModal(){
          this.editEval=false
        },
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
          checkToday(slot){
            if(this.selectedDate==this.today){
                if((slot-2)<this.currentTime.split(':')[0]){
                  return true
                }
                else{
                  return false
                }
            }
            else{
              return false
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
          getRowDiff(item,slots,index){
            if(slots.length>0){
              if((index+1)!=item.row)
              return (item.row-(index+1))
            }
            else{
              return 0
            }

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
           // console.log($('#cl_cleaning_calendar').val())
            this.cleaningDate=$('#cl_cleaning_calendar').val()
            this.combineSlots=[]
            this.slots={}
           // this.slot={}
           this.slot={
            "1":{
              slots:[]
            },
            "2":{
              slots:[]
            },
            "3":{
              slots:[]
            },
            "4":{
              slots:[]
            },
            "5":{
              slots:[]
            },
            "6":{
              slots:[]
            },
            "7":{
              slots:[]
            },
            "8":{
              slots:[]
            }}
            axios.get(this.url+"/agent/cleaningcallendar?cleaning_callendar_date="+this.cleaningDate).then((response) => {
                this.slots = response.data;
                for(var i=0;i<this.slots.notapproved_cleanings.length;i++){
                   
                    this.combineSlots.push({type:'not approved',class:'subscription-cleaning-bg',slots:this.slots.notapproved_cleanings[i]})
                }
                for(var j=0;j<this.slots.appoved_cleanings.length;j++){
                   
                    this.combineSlots.push({type:'approved',class:'onetime-cleaning-bg',slots:this.slots.appoved_cleanings[j]})
                }
                for(var k=0;k<this.slots.followup_cleanings.length;k++){
                    var slot=this.slots.followup_cleanings[k]
                    //this.slots.followup_cleanings[k]['cleaning_hours']=this.slots.followup_cleanings[k].follow_up.cleaning_hours
                    slot.cleaning_hours=slot.follow_up.cleaning_hours
                    slot.order={order_no:slot.follow_up.ticket_no}
                    this.combineSlots.push({type:'followup',class:'followup-cleaning-bg',slots:slot})
                }
                this.parseSlots()
              })
          },
          parseSlots(){
            for(var i=0;i<this.combineSlots.length;i++){
                var startdate=this.combineSlots[i].slots.start_at.split(' ')[0]
                var enddate=this.combineSlots[i].slots.end_at.split(' ')[0]
                var startslot=this.combineSlots[i].slots.start_at.split(' ')[1]+' '+this.combineSlots[i].slots.start_at.split(' ')[2]
                var endslot=this.combineSlots[i].slots.end_at.split(' ')[1]+' '+this.combineSlots[i].slots.end_at.split(' ')[2]
                var slots=[]
                if(startdate==enddate && parseInt(startslot.split(':')[0])%3==0 && parseInt(endslot.split(':')[0])%3==0 && parseInt(startslot.split(':')[1])==0 && parseInt(endslot.split(':')[1])==0){
                  var color=''
                  var slot=moment('12:00 AM', 'h:mma')
                  var limit=moment('11:55 PM', 'h:mma')
                  var beginningTime = moment(startslot, 'h:mma');
                  var endTime = moment(endslot, 'h:mma');
                  if(this.combineSlots[i].type!='followup')
                  {
                  if(this.combineSlots[i].slots.order_scheduler_book.cleaning_policy=='ONE TIME SERVICE'){
                    color='onetime-cleaning-bg'
                  }
                  else if(this.combineSlots[i].slots.order_scheduler_book.cleaning_policy=='SUBSCRIPTION'){
                    color='subscription-cleaning-bg'
                  }
                
                  if(this.combineSlots[i].slots.work_status=='CLEANING_CANCELLED')
                  {
                    color='rejected-bg'
                  }
                }
                  if(this.combineSlots[i].type=='followup')
                  {
                    color='followup-cleaning-bg'
                  }
                  while(slot.isBefore(limit)){
                    if(slot.isBefore(endTime) && slot.isSameOrAfter(beginningTime)){
                      
                      if(slot.isSame(beginningTime) && !(moment(slot).add(3, 'hours')).isSame(endTime)){
                        var slotData={
                          slot:moment(slot).format('hh:mm A'),
                          classType:'cl-start-only',
                          color:color,
                          startTime:startslot,
                          endTime:endslot,
                          startDate:startdate,
                          endDate:enddate,
                          row:'',
                          slots:this.combineSlots[i].slots

                        }
                           
                      }
                      else if(slot.isSame(beginningTime)&& (moment(slot).add(3, 'hours')).isSame(endTime)){
                        var slotData={
                          slot:moment(slot).format('hh:mm A'),
                          classType:'cl-start-end',
                          color:color,
                          startTime:startslot,
                          endTime:endslot,
                          startDate:startdate,
                          endDate:enddate,
                          row:'',
                          slots:this.combineSlots[i].slots
                         

                        }
                           
                      }
                      else if(!slot.isSame(beginningTime) && (moment(slot).add(3, 'hours')).isSame(endTime)){
                        var slotData={
                          slot:moment(slot).format('hh:mm A'),
                          classType:'cl-end-only',
                          color:color,
                          startTime:startslot,
                          endTime:endslot,
                          startDate:startdate,
                          endDate:enddate,
                          row:'',
                          slots:this.combineSlots[i].slots

                        }

                      }
                      else{
                        var slotData={
                          slot:moment(slot).format('hh:mm A'),
                          classType:'cl-continue',
                          color:color,
                          startTime:startslot,
                          endTime:endslot,
                          startDate:startdate,
                          endDate:enddate,
                          row:'',
                          slots:this.combineSlots[i].slots

                        }

                      }
                      console.log("slot data is"+JSON.stringify(slotData))
                      this.parsedSlots.push(slotData)
                      var slotFormatted=moment(slot).format('hh:mm A')
                  console.log("sloformatted is "+slotFormatted)
                  if(slotFormatted=='12:00 AM'){
                    slots.push(1)
                    this.slot["1"].slots.push(slotData)
                  }
                  else if(slotFormatted=='03:00 AM'){
                    slots.push(2)
                    this.slot["2"].slots.push(slotData)
                  }
                  else if(slotFormatted=='06:00 AM'){
                    slots.push(3)
                    this.slot["3"].slots.push(slotData)
                  }
                  else if(slotFormatted=='09:00 AM'){
                    slots.push(4)
                    this.slot["4"].slots.push(slotData)
                  }
                  else if(slotFormatted=='12:00 PM'){
                    slots.push(5)
                    this.slot["5"].slots.push(slotData)
                  }
                  else if(slotFormatted=='03:00 PM'){
                    slots.push(6)
                    this.slot["6"].slots.push(slotData)
                  }
                  else if(slotFormatted=='06:00 PM'){
                    slots.push(7)
                    this.slot["7"].slots.push(slotData)
                  }
                  else if(slotFormatted=='09:00 PM'){
                    slots.push(8)
                    this.slot["8"].slots.push(slotData)
                  }
                      console.log("end time :" +endslot+",start time :"+startslot+",slot :"+moment(slot).format('hh:mm A'))
                  }
                 
                  
                  slot=moment(slot).add(3, 'hours');  
                  }
                  console.log("slots:" +slots)
                  var rowno=this.setRow(slots)
                  console.log("row no:" +rowno)
                  for(var j=0;j<slots.length;j++){
                    var slotind=slots[j]
                    if(this.slot[slotind].slots.length>0){
                      this.slot[slotind].slots[(this.slot[slotind].slots.length-1)].row=rowno
                    }
                   
                  }
                 
                  
                }
            }
          },
          setRow(slots){
           /* var max=this.slot[slots[0]].slots.length
            var rows =[]
            if(max>0)
            {
              for(var j=0;j<max;j++){
                rows.push(this.slot[slots[0]].slots[j].row)
              }
            }*/
            var max=0
            var rows=[]
            
            var maxslots=[]
            for(var i=0;i<slots.length;i++){
              maxslots.push(this.slot[slots[i]].slots.length)
              if(this.slot[slots[i]].slots.length>max){
                max=this.slot[slots[i]].slots.length
                for(var j=0;j<max;j++){
                  rows.push(this.slot[slots[i]].slots[j].row)
                }

              }
            }
            
            console.log("slots are "+JSON.stringify(maxslots)+"max is:" +max)
            if(rows.length>0){
              if(max<(Math.max(...rows)+1)){
                max=Math.max(...rows)+1
              }
              console.log("rows are "+JSON.stringify(rows)+"max is:" +max)
            }
           
            return max
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


