
//$('#cl-evaluator-1').height($('#slot-row-1').height());

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
    $( ".scroll-cal" ).scrollLeft( 650 ); 
    $('#cleaningCalendar-carousel').owlCarousel({
        loop:false,
        margin:10,
        startPosition:4,
        nav:true,
        dots:false,
      
        navText:[`<i class='fa fa-chevron-left service-control' @click='prevService()'></i>`,
      `<i class='fa fa-chevron-right service-control'></i>`], 
        responsive:{
            0:{
                items:2
            },
            600:{
                items:4
            },
            1000:{
                items:5
            },
            1300:{
              items:6
          }
        }
    })
    $('#evalCalendar-carousel').owlCarousel({
      loop:false,
      margin:10,
     
      nav:true,
      dots:false,
      navText:[`<i class='fa fa-chevron-left service-control' @click='prevService()'></i>`,
    `<i class='fa fa-chevron-right service-control'></i>`], 
      responsive:{
          0:{
              items:2
          },
          600:{
              items:4
          },
          1000:{
              items:6
          }
      }
  })
   
  });
  


 
  

var heightCarousel=$('#cleaningCalendar-carousel').height()
$('.owl-item').height(heightCarousel)

  function openModal(){
   
   
  }
  function selectSlot(elem){
   
    $(elem).toggleClass('time-slot-active')
  }


  /** vue js */
  
  var user_type=$('#user_type').val();
 

const app=  new Vue({

    el: '#app',
    vuetify: new Vuetify(),
    delimiters: ['<%', '%>'],
   
    
    data: {
      slotloader:false,
      cal_loader:false,
       user_type:'',
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
        currentSlot:{},
        approved_not_paid:false,
        currentSlotDetails:null,
        openedit:false,
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
        no_of_slots:0,
        teammembers:'yes',
        
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
          "9":{
            slots:[]
          },
          "10":{
            slots:[]
          },
          "11":{
            slots:[]
          },
          "12":{
            slots:[]
          },
        },
        slotFormat:{
          "1":{
            start_time:'12:00 AM',
            end_time:'02:00 AM'
          },
          "2":{
            start_time:'02:00 AM',
            end_time:'04:00 AM'
          },
          "3":{
            start_time:'04:00 AM',
            end_time:'06:00 AM'
          },
          "4":{
            start_time:'06:00 AM',
            end_time:'08:00 AM'
          },
          "5":{
            start_time:'08:00 AM',
            end_time:'10:00 AM'
          },
          "6":{
            start_time:'10:00 AM',
            end_time:'12:00 PM'
          },
          "7":{
            start_time:'12:00 PM',
            end_time:'02:00 PM'
          },
          "8":{
            start_time:'02:00 PM',
            end_time:'04:00 PM'
          },
          "9":{
            start_time:'04:00 PM',
            end_time:'06:00 PM'
          },
          "10":{
            start_time:'06:00 PM',
            end_time:'08:00 PM'
          },
          "11":{
            start_time:'08:00 PM',
            end_time:'10:00 PM'
          },
          "12":{
            start_time:'10:00 PM',
            end_time:'12:00 AM'
          },
         
        },
        new_calendar:true,
        url:'',
       // url:'https://test.bleach-kw.com',
      //   url:'http://localhost:8000',
        //url: 'http://127.0.0.1:8000',
        cleaningData:{
          cleaning_datetime_start:'',
          cleaning_datetime_end:'',
          service_types:[]
        },
        cleaningDetails:{},
        combinedCleaningDetails:[],
        cleaningEditSlots:[],
        availableSlots:[],
        selectedEditSlot:[],
        selectedSlotDetailed:{},
        dataCompleted:false,
        action_type:'edit_cleaning_withoutautofix',
        cleaningAgentDialog:false,
        cleaningFollowupDialog:false,
        followupStat:false,
        convertedDate:'',
        popup:{
          border:'',
          text:'',
          bg:'',
          color:'',
          type:''
        },
        limitdate:'15-07-2021',
        cleaning_duration:[],
            selected_cleaning_duration:{},
            currentServices:[],
            followup_duration:[],
            followup_cleaners:0
           

      },
      watch: {
        services: function (val) {
          
          this.getslotAgain()
        } 
      },
      mounted(){
        this.url = api;
        moment.locale('fr');
        this.currentTime=moment().format().split("T")[1];
        this.dateSelected = moment().format().split("T")[0];
        this.today = moment().format().split("T")[0];
        var urldate=location.href.split('=')[1]
        //this.cleaningDate=urldate.split('-').reverse().join('-')
        //this.selectedDate=urldate.split('-').reverse().join('-')
        var passed_date=location.href.split("cleaning_calendar_date=")[1]
        if(passed_date){
          this.cleaningDate=passed_date
          var dateArray=passed_date.split('-')
          this.selectedDate=dateArray[2]+'-'+dateArray[1]+'-'+dateArray[0]
          $('#cl_cleaning_calendar').val(passed_date)
        }
      
        console.log("cleaning date us "+this.cleaningDate)
       if(!urldate){
         urldate=moment().format().split("T")[0]
       }
       this.calChecker(urldate)
        console.log("today is "+this.today)
        console.log("time is "+this.currentTime)
        this.formatDate()
      if(!passed_date){
        this.parseDate()
      }
      
       
        
       this.getSlots()
       
       
        this.getEvaluationSlots()
      },
      methods:{
        calChecker(date){
          
          
          if(moment(this.limitdate,'DD-MM-YYYY').isSameOrBefore(moment(date,'DD-MM-YYYY'))){
            this.new_calendar=true
          }
          else{
            this.new_calendar=false
           // window.location.href='/evaluator/dashboard/?evaluation_calendar_date='+date
          }
        },
        editCleaningTeam(slot){          
          window.location.href='/common/editcleaning/team/'+slot+'?cleaning_calendar_date='+app.cleaningDate         
        },
        resetCleaningTeam(slot){          
          window.location.href='/common/resetcleaning/team/'+slot         
        },
        // editCleaningTeamOpSupervisor(slot){
        //   window.location.href='/operation-supervisor/editcleaning/team/'+slot  
        // },
        addCleaningTeam(slot){          
          window.location.href='/common/assigncleaning/team/'+slot+'?cleaning_calendar_date='+app.cleaningDate
        },
        // addCleaningTeamOpSupervisor(slot){
        //   window.location.href='/operation-supervisor/assigncleaning/team/'+slot
        // },
        editFollowupTeam(slot){          
          window.location.href='/common/editfollowup/team/'+slot+'?cleaning_calendar_date='+app.cleaningDate         
        },
        // resetFollowupTeam(slot){          
        //   window.location.href='/common/resetfollowup/team/'+slot         
        // },
        // editFollowupTeamOpSupervisor(slot){
        //   window.location.href='/operation-supervisor/editfollowup/team/'+slot  
        // },
        addFollowupTeam(slot){          
          window.location.href='/common/assignfollowup/team/'+slot+'?cleaning_calendar_date='+app.cleaningDate
        },
        // addFollowupTeamOpSupervisor(slot){
        //   window.location.href='/operation-supervisor/assignfollowup/team/'+slot
        // },
        selectEditSlot(slot){
         

          this.selectedEditSlot.push(slot)
          this.selectedSlotDetailed[this.convertedDate].push(slot)
        },
        removeEditSlot(slot){
          const index = this.selectedEditSlot.indexOf(slot);
          if (index > -1) {
            this.selectedEditSlot.splice(index, 1);
          }
          
        },
        closeModal(){
          this.editEval=false
          this.delAlert=false
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
            $('#cl_cleaning_calendar').val(this.cleaningDate)
            
          },
          async getSlots(){
            this.cal_loader=true
           // console.log($('#cl_cleaning_calendar').val())
           $('.owl-item').css('height','auto')
            $('.owl-item').css('min-height','600 px')
           this.services=[]
            this.cleaningDate=$('#cl_cleaning_calendar').val()
           
          
            this.combineSlots=[]
            this.selectedCleaningSlot=[]
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
            },
            "9":{
              slots:[]
            },
            "10":{
              slots:[]
            },
            "11":{
              slots:[]
            },
            "12":{
              slots:[]
            },
            
          }
          
            axios.get(this.url+"/agent/cleaningcallendar?cleaning_callendar_date="+this.cleaningDate).then((response) => {
                this.slots = response.data;
                for(var j=0;j<this.slots.appoved_cleanings.length;j++){

                  this.combineSlots.push({type:'approved',class:'onetime-cleaning-status-bg',slots:this.slots.appoved_cleanings[j]})
                  
                  }
                  for(var k=0;k<this.slots.followup_cleanings.length;k++){
                    var slot=this.slots.followup_cleanings[k]
                    //this.slots.followup_cleanings[k]['cleaning_hours']=this.slots.followup_cleanings[k].follow_up.cleaning_hours
                    slot.cleaning_hours=slot.follow_up.cleaning_hours
                    slot.order={order_no:slot.follow_up.ticket_no}
                    this.combineSlots.push({type:'followup',class:'followup-cleaning-status-bg',slots:slot})
                }
                for(var i=0;i<this.slots.notapproved_cleanings.length;i++){

                  this.combineSlots.push({type:'not approved',class:'subscription-cleaning-bg',slots:this.slots.notapproved_cleanings[i]})

                }

                 this.parseSlots()
                // $(".cl-slot-card").css('min-height',600);

                setTimeout(function(){ 
                  var a = [];
                  console.log("here", $("#div_8").height()) 
                  a.push($("#div_1").height()+10)
                  a.push($("#div_2").height()+10)
                  a.push($("#div_3").height()+10)
                  a.push($("#div_4").height()+10)
                  a.push($("#slot-start").height()+10)
                  a.push($("#div_6").height()+10)
                  a.push($("#div_7").height()+10)
                  a.push($("#div_8").height()+10)
                  a.push($("#div_9").height()+10)
                  a.push($("#div_10").height()+10)
                  a.push($("#div_11").height()+10)
                  a.push($("#div_12").height()+10)
                 var m = a[0];
                  for(var q=0;q<a.length;q++){
                    console.log(a[q],'height')
                    if(a[q]>=m){
                      m = a[q]
                    }
                  }
                  
                  $('.owl-item').height(m+200)
                  $('.cl-slot-card').css('height','100%')
              
                }, 500);
                this.cal_loader=false
                
              })
          },
          getSlotDetails(slot){
            var prevSlot=parseInt(slot)-1
            var nextSlot=parseInt(slot)+1
           if(!this.selectedCleaningSlot.includes(String(prevSlot)) && !this.selectedCleaningSlot.includes(String(nextSlot)) && this.selectedCleaningSlot.length>0)
            {
              this.selectedCleaningSlot=[]
              this.selectedCleaningSlot.push(String(slot))
            }
            
            var max=Math.max(...this.selectedCleaningSlot)
            var min=Math.min(...this.selectedCleaningSlot)
            if(this.slotFormat[min].start_time){
              this.cleaningData.cleaning_datetime_start=this.cleaningDate+' '+this.slotFormat[min].start_time
            }
            if(this.slotFormat[max].end_time){
              if(this.slotFormat[max].end_time=='12:00 AM'){
                this.cleaningData.cleaning_datetime_end=moment(this.cleaningDate,'DD-MM-YYYY').add(1,'days').format('DD-MM-YYYY')+' '+this.slotFormat[max].end_time
              }
              else{
                this.cleaningData.cleaning_datetime_end=this.cleaningDate+' '+this.slotFormat[max].end_time
              }
              
            }
           
           
            this.cleaningData.service_types=this.services

           /* for(var i=0;i<this.selectedCleaningSlot.length;i++){
              if(this.slot[this.selectedCleaningSlot[i]].slots.length>0)
              {
                var index=this.selectedCleaningSlot[i]
              this.cleaningData.cleaning_datetime_start=this.slot[index].slots[0].slots.start_at
              this.cleaningData.cleaning_datetime_end=this.slot[index].slots[0].slots.end_at
              console.log("start:"+this.cleaningData.cleaning_datetime_start,"end:"+this.cleaningData.cleaning_datetime_end)
              this.cleaningData.service_types=["General Cleaning"]
              axios.post(this.url+"/agent/cleaningcallendar/availability/",this.cleaningData).then((response) => {

              })
            }
            }*/
            axios.post(this.url+"/agent/cleaningcallendar/availability/",this.cleaningData).then((response) => {
              this.cleaningDetails=response.data
            })
            
          },
          getslotAgain(){
            
           
           
            this.cleaningData.service_types=this.services
            axios.post(this.url+"/agent/cleaningcallendar/availability/",this.cleaningData).then((response) => {
              this.cleaningDetails=response.data
            })
          
          },
          checkslot(index){
            var no_of_slots=this.selected_cleaning_duration.cleaning_hours/2
            if(this.selectedEditSlot.length<no_of_slots)
            {
            if(this.selectedEditSlot.length>0)
            {
            if(index==0){
              var nextslot=this.availableSlots[(index+1)]
              if(this.selectedEditSlot.includes((nextslot.split(' ')[0]+' '+nextslot.split(' ')[1]))){
                return true
              }
              else{
                return false
              }
            }
            else if(index==(this.availableSlots.length-1)){
              var prevslot=this.availableSlots[(index-1)]
              if(this.selectedEditSlot.includes((prevslot.split(' ')[0]+' '+prevslot.split(' ')[1]))){
                return true
              }
              else{
                return false
              }
            }
            else{  
              var prevslot=this.availableSlots[(index-1)]
            var nextslot=this.availableSlots[(index+1)]
            
            if(this.selectedEditSlot.includes((prevslot.split(' ')[0]+' '+prevslot.split(' ')[1]))||this.selectedEditSlot.includes((nextslot.split(' ')[0]+' '+nextslot.split(' ')[1]))){
              return true
            }
            else{
              return false
            }
          }
        }
          else{
            return true
          }
        }
        else{
          return false
        }
          },
          durationCalculator(){
            this.cleaning_duration=[]
            this.selected_cleaning_duration={}
            if(this.currentSlotDetails.cleaning_hours)
            {
            
            var cleaning_hours=this.currentSlotDetails.cleaning_hours
            var no_of_cleaners=this.currentSlotDetails.no_of_cleaners
            var prod=cleaning_hours*no_of_cleaners
            console.log("productivity :"+prod)
            for(var i=2;i<=10;i=i+2){
             
              var cleaning_hour=i
              var cleaner=Math.round(prod/cleaning_hour)
              if(cleaner<1){
                cleaner=1
              }
              console.log("cleaning hr :"+i+"productivity:"+prod+"cleaners"+cleaner+"i is"+i)
              this.cleaning_duration.push({
                cleaning_hours:cleaning_hour,
                no_of_cleaners:cleaner

              })
              if(cleaning_hour==this.currentSlotDetails.cleaning_hours){
                this.selected_cleaning_duration={
                  cleaning_hours:cleaning_hour,
                  no_of_cleaners:cleaner
                }
              }
            }
           /* if(cleaning_hours>2){
              var cleaning_hour1=cleaning_hours-2
              var cleaning_hour3=cleaning_hours+2
            }
            else{
              var cleaning_hour1=cleaning_hours+2
              var cleaning_hour3=cleaning_hours+4
            }
              var cleaner_1=Math.round(prod/cleaning_hour1)
              var cleaner_3=Math.round(prod/cleaning_hour3)
              if(cleaner_1<=0){
                cleaner_1=1
              }
              if(cleaner_3<=0){
                cleaner_3=1
              }
              this.cleaning_duration.push({
                cleaning_hours:cleaning_hour1,
                no_of_cleaners:cleaner_1,

              })
              this.cleaning_duration.push({
                cleaning_hours:cleaning_hours,
                no_of_cleaners:no_of_cleaners, 
              })
              this.cleaning_duration.push({
                cleaning_hours:cleaning_hour3,
                no_of_cleaners:cleaner_3,
              })
              this.selected_cleaning_duration={
                cleaning_hours:cleaning_hours,
                no_of_cleaners:no_of_cleaners
              }*/
            }
            else{
              this.currentSlotDetails.cleaning_hours=0
              this.currentSlotDetails.no_of_cleaners=0
            }
              
            
          },
          selectDuration(duration){
            this.selected_cleaning_duration=duration
            this.editCleaning()
          },
          selectFollowupDuration(duration){
            duration.no_of_cleaners=this.followup_cleaners
            this.selected_cleaning_duration=duration
           
            this.editFollowupCleaning()
          },
          editCleaning(){
            var service_type=[]
            for(var i=0;i<this.currentServices.length;i++){
              service_type.push(this.currentServices[i].order_scheduler_book.service_type.name)
            }
            
            var temparray=this.selectedDate.split("-")
            var selectedDate=temparray.reverse().join("-")
            this.convertedDate=selectedDate
            this.selectedEditSlot=[]
            if(!this.selectedSlotDetailed[this.convertedDate]){
              this.selectedSlotDetailed[this.convertedDate]=[]
            }
          
            this.editEval=true
            axios.post(this.url+'/agent/cleaningcallendar/cleaning/edit/slotes/',{
             // cleaning_date:this.currentSlotDetails.start_at.split(' ')[0],
             

             cleaning_date:selectedDate,
              number_of_cleaners:this.selected_cleaning_duration.no_of_cleaners,
              service_types:service_type,
              evaluation_id:this.currentSlotDetails.order.order_no
            }).then((response) => {
              this.cleaningEditSlots=response.data.slotes

              this.parseEditSlots()
            })
          },
          editFollowupCleaning(){
            
            this.editEval=true
            this.selectedEditSlot=[]
            var temparray=this.selectedDate.split("-")
            var selectedDate=temparray.reverse().join("-")
            this.convertedDate=selectedDate
            if(!this.selectedSlotDetailed[this.convertedDate]){
              this.selectedSlotDetailed[this.convertedDate]=[]
            }
            this.slotloader=true
            axios.post(this.url+'/agent/cleaningcallendar/cleaning/edit/slotes/',{
              // cleaning_date:this.currentSlotDetails.start_at.split(' ')[0],
              
              
              cleaning_date:selectedDate,
               number_of_cleaners:this.selected_cleaning_duration.no_of_cleaners,
               service_types:[],
               evaluation_id:this.currentSlotDetails.follow_up.ticket_no
             }).then((response) => {
              this.slotloader=false
               this.cleaningEditSlots=response.data.slotes
 
               this.parseEditSlots()
             })
            /*this.cleaningEditSlots={
              "0":[3,6,9,12],
              "3":[3,6,9,12],
              "6":[3,6,9,12],
              "9":[3,6,9,12],
              "12":[3,6,9,12],
              "15":[3,6,9,12],
              "18":[3,6,9,12],
              "21":[3,6,9,12]

            }*/
            
           
          },
          saveEdit(){
            var schedules=[]
            var serviceTypes=[]
            for(var sh=0;sh<this.currentServices.length;sh++){
              schedules.push(this.currentServices[sh].id)
              serviceTypes.push(this.currentServices[sh].order_scheduler_book.service_type.name)
            }
            var temparray=this.selectedDate.split("-")
            var selectedDate=temparray.reverse().join("-")
            var max=moment(this.selectedEditSlot[0], 'h:mma')
            var min=moment(this.selectedEditSlot[0], 'h:mma')
            for(var i=1;i<this.selectedEditSlot.length;i++){
              var cslot=moment(this.selectedEditSlot[i], 'h:mma')
              if(moment(cslot).isAfter(max)){
                max=cslot
              }
              if(moment(cslot).isBefore(min)){
                min=cslot
              }
            }
           
            var end = (moment(max).add(2, 'hours'))

            axios.post(this.url+'/agent/cleaningcallendar/cleaning/edit/save/',{
             // cleaning_date:this.currentSlotDetails.start_at.split(' ')[0],
             

            cleaning_start:selectedDate+' '+moment(min).format('hh:mm A'),
            cleaning_end:selectedDate+' '+moment(end).format('hh:mm A'),
            no_of_cleaners:this.selected_cleaning_duration.no_of_cleaners,
            cleaning_hours:this.selected_cleaning_duration.cleaning_hours,
            schedules : schedules,
            evaluation_id:this.currentSlotDetails.order.order_no,
            service_types:serviceTypes,
            action_type:this.action_type
            }).then((response) => {
             
              this.editEval=false,
              this.selectedEditSlot=[],
              this.availableSlots=[],
              this.currentSlot={},
              this.currentSlotDetails={}
              this.cleaningAgentDialog=false
              this.dataCompleted=false
              this.getSlots()
              
            })
          },
          saveEditFollowup(){
           
            var temparray=this.selectedDate.split("-")
            var selectedDate=temparray.reverse().join("-")
            var max=moment(this.selectedEditSlot[0], 'h:mma')
            var min=moment(this.selectedEditSlot[0], 'h:mma')
            for(var i=1;i<this.selectedEditSlot.length;i++){
              var cslot=moment(this.selectedEditSlot[i], 'h:mma')
              if(moment(cslot).isAfter(max)){
                max=cslot
              }
              if(moment(cslot).isBefore(min)){
                min=cslot
              }
            }
         
            var end = (moment(max).add(2, 'hours'))

            axios.post(this.url+'/agent/cleaningcallendar/followup/edit/save/',{
          
             

            cleaning_start_at:selectedDate+' '+moment(min).format('hh:mm A'),
            cleaning_end_at:selectedDate+' '+moment(end).format('hh:mm A'),
            no_of_cleaners:this.selected_cleaning_duration.no_of_cleaners,
            cleaning_hours:this.selected_cleaning_duration.cleaning_hours,
            followup_id:this.currentSlotDetails.id
            }).then((response) => {
           

              this.editEval=false,
              this.selectedEditSlot=[],
              this.availableSlots=[],
              this.currentSlot={},
              this.currentSlotDetails={}
              this.cleaningFollowupDialog=false
              this.followupStat=false
              this.getSlots()
              
            })
          },
          followupDuration(){
            this.followup_duration=[]
            for(var i=2;i<=10;i=i+2)
            {
            this.followup_duration.push({
              no_of_cleaners:this.followup_cleaners,
              cleaning_hours:i
            })
          }
          },
          parseEditSlots(){
            this.availableSlots=[]
              for(var slot in this.cleaningEditSlots){

                if(this.cleaningEditSlots[slot].includes(2))
                {
                 
                  
                   var slotno=(parseInt(slot)/2)+1
                    var start=this.slotFormat[slotno].start_time
                    var end=this.slotFormat[slotno].end_time
                   
                    var slotAvailable=start+' - '+end
                  
                  this.availableSlots.push(slotAvailable)
                }
                
              }
          },
          checkCustomerBooking(classType,slot,type){
            if(type!="followup-cleaning-status-bg"){

            
            if(classType=='cl-start-end' || classType=='cl-end-only')
            {
            if (slot.evaluation_details.evaluation.booking_evaluation.length>0){
              if(slot.evaluation_details.evaluation.booking_evaluation[0].booking_type=='CLEANINGBOOKING')
              {
                return true
              }
              else{
                return false
              }
              
            }
            else{
              return false
            }
          }
          else{
            return false
          }
        }
        else{
          return false
        }
          },
          checkTeamLeader(slot,type){
            if(type!='followup-cleaning-status-bg'){
              if(slot.cleaning_team_order_scheduler.length>0){
                if(slot.cleaning_team_order_scheduler[0].team_leader){
                 return  true
                }
                else{
                  return false
                }
              }
              else{
                return false
              }
            }
            else{
              if(slot.followupteam_followupschedule.length>0){
                if(slot.followupteam_followupschedule[0].team_leader){
                  return  true
                 }
                 else{
                   return false
                 }
              }
              else{
                return false
              }
            }
            
          },
          closeCleaningModal(){
            this.editEval=false
            this.cleaningAgentDialog=false
            this.cleaningFollowupDialog=false
          },
          openCleaningModal(item){
            
            this.cleaningAgentDialog=false
            this.dataCompleted=false
            this.cleaningFollowupDialog=false
              this.followupStat=false
            this.currentSlotDetails={}
            //this.dataCompleted=true
            
            
         if(item.color!='followup-cleaning-status-bg')
         {
          if(item.color=='subscription-cleaning-status-bg'){
            this.popup.color='#139275'
            this.popup.border='subscription-border'
            this.popup.type='subscription-popup'
            this.popup.text='subscription-text',
            this.popup.bg='subscription-cleaning-status-bg'


          }
          else if(item.color=='onetime-cleaning-status-bg'){
            this.popup.color='#0D87C5'
            this.popup.border='onetime-border'
            this.popup.type='onetime-popup'
            this.popup.text='onetime-text',
            this.popup.bg='onetime-cleaning-status-bg'
          }
          else if(item.color=='approved-notpaid-status-bg'){
            this.popup.color='#699189'
            this.popup.border='approved-notpaid-border'
            this.popup.type='approved-notpaid-popup'
            this.popup.text='approved-notpaid-text',
            this.popup.bg='approved-notpaid-status-bg'
          }
          else if(item.color=='not-approved-status-bg'){
            this.popup.color='#8B8B8B'
            this.popup.border='not-approved-border'
            this.popup.type='not-approved-popup'
            this.popup.text='not-approved-text',
            this.popup.bg='not-approved-status-bg'
          }
           
            axios.get(this.url+"/agent/cleaningcallendar/cleaning/popup/?cleaning_start="+item.slots.start_at+'&cleaning_end='+item.slots.end_at+'&evaluation_id='+item.slots.order.order_no).then((response) => {
              this.approved_not_paid =response.data.approved_not_paid
              this.currentSlotDetails=response.data.cleaning_details[0]
              this.currentServices=response.data.cleaning_details
              this.no_of_slots=parseInt(this.currentSlotDetails.cleaning_hours)/2
              this.cleaningAgentDialog=true
              this.dataCompleted=true
              this.durationCalculator()
              
            })
          }
          else{
         

          
            axios.get(this.url+"/agent/cleaningcallendar/followupcleaning/popup/?followup_scheduler_id="+item.slots.id).then((response) => {
              this.followupDuration()
              this.currentSlotDetails=response.data.followup_cleanings[0]
              this.followup_cleaners=this.currentSlotDetails.follow_up.no_of_cleaners
              this.selected_cleaning_duration={
                cleaning_hours:this.currentSlotDetails.follow_up.cleaning_hours,
                no_of_cleaners:this.currentSlotDetails.follow_up.no_of_cleaners
              }
              this.currentServices=response.data.followup_cleanings
              this.no_of_slots=parseInt(this.currentSlotDetails.follow_up.cleaning_hours)/3   
              this.cleaningFollowupDialog=true
              this.followupStat=true
             // this.durationCalculator()
             
               
            
              
            })
          }
          this.currentSlot=item
            

          },
          changeFollowupCleaners(){
            this.selected_cleaning_duration.no_of_cleaners=parseInt(this.followup_cleaners)
            this.editFollowupCleaning()
          },
          async parseSlots(){
            for(var i=0;i<this.combineSlots.length;i++){
                var startdate=this.combineSlots[i].slots.start_at.split(' ')[0]
                var enddate=this.combineSlots[i].slots.end_at.split(' ')[0]
                var startslot=this.combineSlots[i].slots.start_at.split(' ')[1]+' '+this.combineSlots[i].slots.start_at.split(' ')[2]
                var endslot=this.combineSlots[i].slots.end_at.split(' ')[1]+' '+this.combineSlots[i].slots.end_at.split(' ')[2]
                var slots=[]
                if(parseInt(startslot.split(':')[0])%2==0 && parseInt(endslot.split(':')[0])%2==0 && parseInt(startslot.split(':')[1])==0 && parseInt(endslot.split(':')[1])==0){
                  var color=''
                  var slot=moment(this.cleaningDate,'DD-MM-YYYY HH:mm A')
               //   var limit=moment(startdate+' 12:00 AM').format('DD MM YYYY h:mm:ss a').add(1,'days')
                  var limit =moment(this.cleaningDate,'DD-MM-YYYY HH:mm A').add(1, 'days')
                 // var lastday =moment(this.cleaningDate,'DD-MM-YYYY HH:mm A').(1, 'days')
                  
                  
                  
                
                  var date_start=this.combineSlots[i].slots.start_at
                  var date_end=this.combineSlots[i].slots.end_at
                  /*var beginningTime = moment(startslot, 'h:mma');
                  var endTime = moment(endslot, 'h:mma');*/
               
                  var beginningTime=moment(date_start,'DD-MM-YYYY HH:mm A')
                  var endTime=moment(date_end,'DD-MM-YYYY HH:mm A')
                 

                  if(this.combineSlots[i].type=='followup')
                  {
                    color='followup-cleaning-status-bg'
                  }
                  else if(this.combineSlots[i].type=='not approved'){
                    if(this.combineSlots[i].slots.order.payment_status == 'PENDING' && this.combineSlots[i].slots.order.order_status == 'None')
                    {
                      color='not-approved-status-bg' // + disable
                    }
                    else if(this.combineSlots[i].slots.order.payment_status == 'PENDING' && this.combineSlots[i].slots.order.order_status == 'APPROVED_BY_CLIENT')
                    {
                      color='approved-notpaid-status-bg' //+ disable
                    }else{
                      color='not-approved-status-bg' //+ disable 
                    }
                  }
                  else if(this.combineSlots[i].type=='approved'){
                    if(this.combineSlots[i].slots.work_status=='CLEANING_CANCELLED')
                        {
                          color='rejected-status-bg' //+ disable, number disable
                        }
                    else if(this.combineSlots[i].slots.order_scheduler_book.cleaning_policy=='ONE TIME SERVICE'){
                          color='onetime-cleaning-status-bg'
                        }
                    else if(this.combineSlots[i].slots.order_scheduler_book.cleaning_policy=='SUBSCRIPTION'){
                          color='subscription-cleaning-status-bg'
                        }
                  }
                  
                  while(slot.isBefore(limit)){
                    if(slot.isBefore(endTime) && slot.isSameOrAfter(beginningTime)){
                      
                      if(slot.isSame(beginningTime) && !(moment(slot).add(2, 'hours')).isSame(endTime)){
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
                      else if(slot.isSame(beginningTime)&& (moment(slot).add(2, 'hours')).isSame(endTime)){
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
                      else if(!slot.isSame(beginningTime) && (moment(slot).add(2, 'hours')).isSame(endTime)){
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
                      if(slotData.color=='not-approved-status-bg'){
                          this.parsedSlots.push(slotData)
                          var slotFormatted=moment(slot).format('hh:mm A')
                    
                      if(slotFormatted=='12:00 AM'){
                        slots.push(1)
                        this.slot["1"].slots.push(slotData)
                      }
                      else if(slotFormatted=='02:00 AM'){
                        slots.push(2)
                        this.slot["2"].slots.push(slotData)
                      }
                      else if(slotFormatted=='04:00 AM'){
                        slots.push(3)
                        this.slot["3"].slots.push(slotData)
                      }
                      else if(slotFormatted=='06:00 AM'){
                        slots.push(4)
                        this.slot["4"].slots.push(slotData)
                      }
                      else if(slotFormatted=='08:00 AM'){
                        slots.push(5)
                        this.slot["5"].slots.push(slotData)
                      }
                      else if(slotFormatted=='10:00 AM'){
                        slots.push(6)
                        this.slot["6"].slots.push(slotData)
                      }
                      else if(slotFormatted=='12:00 PM'){
                        slots.push(7)
                        this.slot["7"].slots.push(slotData)
                      }
                      else if(slotFormatted=='02:00 PM'){
                        slots.push(8)
                        this.slot["8"].slots.push(slotData)
                      }
                      else if(slotFormatted=='04:00 PM'){
                        slots.push(9)
                        this.slot["9"].slots.push(slotData)
                      }
                      else if(slotFormatted=='06:00 PM'){
                        slots.push(10)
                        this.slot["10"].slots.push(slotData)
                      }
                      else if(slotFormatted=='08:00 PM'){
                        slots.push(11)
                        this.slot["11"].slots.push(slotData)
                      }
                      else if(slotFormatted=='10:00 PM'){
                        slots.push(12)
                        this.slot["12"].slots.push(slotData)
                      }
                      }
                      else{
                        
                      
                  
                      this.parsedSlots.push(slotData)
                      var slotFormatted=moment(slot).format('hh:mm A')
                
                  if(slotFormatted=='12:00 AM'){
                    slots.push(1)
                    this.slot["1"].slots.push(slotData)
                  }
                  else if(slotFormatted=='02:00 AM'){
                    slots.push(2)
                    this.slot["2"].slots.push(slotData)
                  }
                  else if(slotFormatted=='04:00 AM'){
                    slots.push(3)
                    this.slot["3"].slots.push(slotData)
                  }
                  else if(slotFormatted=='06:00 AM'){
                    slots.push(4)
                    this.slot["4"].slots.push(slotData)
                  }
                  else if(slotFormatted=='08:00 AM'){
                    slots.push(5)
                    this.slot["5"].slots.push(slotData)
                  }
                  else if(slotFormatted=='10:00 AM'){
                    slots.push(6)
                    this.slot["6"].slots.push(slotData)
                  }
                  else if(slotFormatted=='12:00 PM'){
                    slots.push(7)
                    this.slot["7"].slots.push(slotData)
                  }
                  else if(slotFormatted=='02:00 PM'){
                    slots.push(8)
                    this.slot["8"].slots.push(slotData)
                  }
                  else if(slotFormatted=='04:00 PM'){
                    slots.push(9)
                    this.slot["9"].slots.push(slotData)
                  }
                  else if(slotFormatted=='06:00 PM'){
                    slots.push(10)
                    this.slot["10"].slots.push(slotData)
                  }
                  else if(slotFormatted=='08:00 PM'){
                    slots.push(11)
                    this.slot["11"].slots.push(slotData)
                  }
                  else if(slotFormatted=='10:00 PM'){
                    slots.push(12)
                    this.slot["12"].slots.push(slotData)
                  }
                  
                 
                   
                  }
                }
                  
                  slot=moment(slot).add(2, 'hours');  
                  }
                 console.log("row uis"+slots+"slotformatted is "+slotFormatted)
       
                  var rowno=this.setRow(slots)
                  console.log("row no "+rowno)
                  for(var j=0;j<slots.length;j++){
                    var slotind=slots[j]
                    if(this.slot[slotind].slots.length>0){
                      this.slot[slotind].slots[(this.slot[slotind].slots.length-1)].row=rowno
                    }
                   
                  }
                  
                  
                }
                
                
                /*    continous slot */
             /*   else{
                  if(this.combineSlots[i].type!='followup')
                  {
                  if(this.combineSlots[i].slots.order_scheduler_book.cleaning_policy=='ONE TIME SERVICE'){
                    color='onetime-cleaning-status-bg'
                  }
                  else if(this.combineSlots[i].slots.order_scheduler_book.cleaning_policy=='SUBSCRIPTION'){
                    color='subscription-cleaning-status-bg'
                  }
                
                  if(this.combineSlots[i].slots.work_status=='CLEANING_CANCELLED')
                  {
                    color='rejected-status-bg'
                  }
                }
                  if(this.combineSlots[i].type=='followup')
                  {
                    color='followup-cleaning-status-bg'
                  }
                  else if(this.combineSlots[i].type=='not approved'){
                    if(!this.combineSlots[i].slots.order.order_status)
                    {
                      color='not-approved-notpaid-status-bg'
                    }
                    else{
                      color='approved-notpaid-status-bg'
                    }
                  }
                  else if(this.combineSlots[i].type=='approved'){
                    if(!this.combineSlots[i].slots.order.order_status)
                    {
                      color='approved-notpaid-status-bg'
                    }
                   
                  }



                }*/
               
            }

           
          },
          setRow(slots){
           
            var max=0
            var rows=[]
            var maxrow=0
            var maxslots=[]
            for(var i=0;i<slots.length;i++){
              maxslots.push(this.slot[slots[i]].slots.length) 
             
                max=this.slot[slots[i]].slots.length 
                for(var j=0;j<max;j++){
                  rows.push(this.slot[slots[i]].slots[j].row) 
                }

            
            }
            
          
            if(rows.length>0){
           
                maxrow=Math.max(...rows)+1
              
              
            
            }
           
            return maxrow
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
           

          }
      }
  })

  app.user_type=user_type
  console.log("user is "+user_type)
  //New Date picker
  $('.next-day-calendar').on('click', function () {

    $selectedDay            = moment($('#cl_cleaning_calendar').val(),'DD-MM-YYYY').valueOf();
   // console.log("selected day is "+$selectedDay+"other is" + moment($('#cl_cleaning_calendar').val(),'DD-MM-YYYY').valueOf())
    var $tmpSelectedDay     = new Date($selectedDay) 
    $tmpSelectedDay.setDate($tmpSelectedDay.getDate() + 1);
    $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
        
 });


$('.prev-day-calendar').on('click', function () {
  $selectedDay=moment($('#cl_cleaning_calendar').val(),'DD-MM-YYYY').valueOf()
   // $selectedDay            = $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").getDate();
    var $tmpSelectedDay     = new Date($selectedDay) 
    $tmpSelectedDay.setDate($tmpSelectedDay.getDate() - 1);
    $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));

});

$('.today-date').on('click', function () {
    var $tmpSelectedDay     = new Date();
    $(this).parent('.date-wrapper-inner').children('.date_pick').data("DateTimePicker").setDate(moment($tmpSelectedDay).format('DD-MM-YYYY'));
});

function load_cleaning_data(){
  
  console.log(JSON.stringify(app.slots.appoved_cleanings),"cln data")
  
  var approved_cleaning_ids=[]

  for(var i=0;i<app.slots.appoved_cleanings.length;i++){

    approved_cleaning_ids.push(app.slots.appoved_cleanings[i].id)

  }

  console.log(approved_cleaning_ids,"clnids")

  $('#id_cleaningids').val(approved_cleaning_ids);
  $('#id_cleaningsdate').val($('#cl_cleaning_calendar').val());
  
  // let json=JSON.stringify(approved_cleaning_ids)
  // post_data={json_data:approved_cleaning_ids}
  // console.log(post_data,"pos")

  // axios.post(this.url+"/api/cleaning-export/",post_data )
  //   .then((response) => {
  //       console.log(response,"gone")
  //       if(response.data['ERROR']){
  //         this.errMsg=response.data['ERROR']
  //       }
 
  //     //this.parseSize();
  //   })
  //     .catch((error) => {
  //     console.log(error);
  //   });
}


