
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
      },
      methods:{
          getSlots(){
            axios.get(this.url+"/agent/cleaningcallendar?cleaning_callendar_date=28-05-2021").then((response) => {
                this.slots = response.data;
                for(var i=0;i<this.slots.notapproved_cleanings.length;i++){
                    this.combineSlots.push({type:'not approved',slots:this.slots.notapproved_cleanings[i]})
                }
                for(var j=0;i<this.slots.appoved_cleanings.length;j++){
                    this.combineSlots.push({type:'approved',slots:this.slots.appoved_cleanings[j]})
                }
                for(var k=0;i<this.slots.followup_cleanings.length;k++){
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

            
          }
      }
  })

