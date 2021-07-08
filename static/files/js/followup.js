
let app=  new Vue({
  el: '#app',
  delimiters: ['<%', '%>'],
  vuetify: new Vuetify({theme: {
      themes: {
        light: {
          primary: '#2f4e85', // #E53935
          secondary: '#FFCDD2', // #FFCDD2
          accent: '#3F51B5', // #3F51B5
        },
      },
    }}),
    mounted(){
        this.today = moment().format().split("T")[0];
this.dateSelected=moment().format().split("T")[0];
console.log("today us"+this.dateSelected)
this.selected_slots[this.dateSelected]={
  slots:[]
}
    },
    data:{
        time_slots_selected:[],
        schedule_err_msg:"",
        dateSelected:'',
        today:'',
        slot_dialog:false,
        render:true,
        time_slots:[
        {
  start_time:'12:00 AM',
  end_time:'02:00 AM'
},{
  start_time:'02:00 AM',
  end_time:'04:00 AM'
},
{
  start_time:'04:00 AM',
  end_time:'06:00 AM'
},
{
  start_time:'06:00 AM',
  end_time:'08:00 AM'
},
{
  start_time:'08:00 AM',
  end_time:'10:00 AM'
},
{
  start_time:'10:00 AM',
  end_time:'12:00 PM'
},
{
  start_time:'12:00 PM',
  end_time:'02:00 PM'
},
{
  start_time:'02:00 PM',
  end_time:'04:00 PM'
},
{
  start_time:'04:00 PM',
  end_time:'06:00 PM'
},
{
  start_time:'06:00 PM',
  end_time:'08:00 PM'
},
{
  start_time:'08:00 PM',
  end_time:'10:00 PM'
},
{
  start_time:'10:00 PM',
  end_time:'12:00 AM'
}
        ],
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
selected_slots:{}
    },
    methods:{
        confirmSlot(){
            this.time_slots_selected=[]
            var counter=1
            for(var i in this.selected_slots){
              if(this.selected_slots[i].slots.length>0)
              {
                var min=Math.min( ...this.selected_slots[i].slots )
                var max=Math.max( ...this.selected_slots[i].slots )
                var year=i.split('-')[0]
                var month=i.split('-')[1]
                var day=i.split('-')[2]
                var date=day+'-'+month+'-'+year
                this.time_slots_selected.push({
                    date:date,
                    cleaning_hours:this.selected_slots[i].slots.length*2,
                    starting_time:this.slotFormat[min].start_time
                })
              }
            }
            this.slot_dialog=false
            this.selected_slots={}
            this.dateSelected=this.today
            this.selected_slots[this.today]={
                      slots:[]
                }


            var cleaningdates = "";
            var cleaninghours = 0;
            var cleaningtime = "0";
              $.each(this.time_slots_selected,function(key,value){
                cleaningdates += value.date+"," ;
                cleaninghours += value.cleaning_hours;
                if (key == 0){
                cleaningtime = value.starting_time;
                }
              })
            cleaningdates = cleaningdates.replace(/,\s*$/, "");
            
            $('#id_cleaning_hours').val(cleaninghours);
            $('#id_tendative_date').val(cleaningdates);
            $('#id_tendative_time').val(cleaningtime);

            
        },
        resetSlots(){
            this.slot_dialog=false
            this.selected_slots={}
            this.dateSelected=this.today
            this.selected_slots[this.today]={
                      slots:[]
                }
        },
        dateChange(){
            if(!this.selected_slots[this.dateSelected]){
          this.selected_slots[this.dateSelected]={
            slots:[]
          }
        }
        },
        addSlot(start,end,slot){
this.render=false
  this.selected_slots[this.dateSelected].slots.push(slot)
  this.render=true
},
removeSlot(slot){
this.render=false
var prevSlot=parseInt(slot)-1
var nextSlot=parseInt(slot)+1
var index=this.selected_slots[this.dateSelected].slots.indexOf(slot)
this.selected_slots[this.dateSelected].slots.splice(index,1)
if(this.selected_slots[this.dateSelected].slots.includes(nextSlot)&&this.selected_slots[this.dateSelected].slots.includes(prevSlot))
{
  var tempSlots=[...this.selected_slots[this.dateSelected].slots]
  for(var i=0;i<this.selected_slots[this.dateSelected].slots.length;i++){
    if(this.selected_slots[this.dateSelected].slots[i]>slot){
      var slotindex=tempSlots.indexOf(this.selected_slots[this.dateSelected].slots[i])
      tempSlots.splice(slotindex,1)
    }
  }
//  console.log("duble slot is "+this.selected_double_slots+"tempslot:"+tempSlots)
  this.selected_slots[this.dateSelected].slots=[...tempSlots]

}
this.render=true
},
checkSlotStat(slot){
  var prevSlot=parseInt(slot)-1
  var nextSlot=parseInt(slot)+1
  var counter=0
  for(var i in this.selected_slots){
    counter=counter+this.selected_slots[i].slots.length
  }
  
  if(this.selected_slots[this.dateSelected].slots.length>0)
  {
  if(slot==1){
    if(this.selected_slots[this.dateSelected].slots.includes(nextSlot)){
      return true
    }
    else {
      return false
    }
  }
  else if(slot==12){
    if(this.selected_slots[this.dateSelected].slots.includes(prevSlot)){
      return true
    }
    else {
      return false
    }
  }
  else{
    if(this.selected_slots[this.dateSelected].slots.includes(prevSlot)||this.selected_slots[this.dateSelected].slots.includes(nextSlot))
    {
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

},
slotCounter(){
  var counter=0
  for(var i in this.selected_slots){
    counter=counter+this.selected_slots[i].slots.length
  }
  return counter
},
    }
})



    
  