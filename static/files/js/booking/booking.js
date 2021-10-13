$(document).ready(function(){
  
  $('#category-carousel').owlCarousel({
    loop:false,
    
    responsiveClass:true,
    responsive:{
        0:{
            items:1,
            nav:false
        },
        600:{
            items:4,
            nav:false
        },
        1000:{
            items:5,
            nav:false,
            loop:false
        }
    }
});
$('#service-carousel').owlCarousel({
    loop:false,
    
    responsiveClass:true,
    navText:["<i class='fa fa-chevron-left service-control' @click='prevService()'></i>",
    "<i class='fa fa-chevron-right service-control'></i>"],
    responsive:{
        0:{
            items:1,
            nav:false,
            loop:true
        },
        600:{
            items:4,
            nav:false
        },
        1000:{
            items:5,
            nav:true,
            loop:false
        }
    }
});

  



selectServiceOnly('General Cleaning')




});

function selectService(item,itempt){
  
  $('#service-carousel').find('.active-icon').replaceWith(`
  <i class="far fa-circle inactive-icon"></i>
  `)
  $(itempt).find('.inactive-icon').replaceWith(` <i
  class="fa fa-check-circle active-icon"
></i>`)
app.selectService({name:item})

}
function selectServiceOnly(service){
  app.selectService({name:service})
  
  $('#service-carousel').find('.active-icon').replaceWith(`
  <i class="far fa-circle inactive-icon"></i>
  `)
  $('.service-one').find('.inactive-icon').replaceWith(` <i
  class="fa fa-check-circle active-icon"
></i>`)


}

const app=new Vue({
    el: '#app',
    delimiters: ['<%', '%>'],
    vuetify: new Vuetify({theme: {
        themes: {
          light: {
            primary: '#2e4e85', // #E53935
            secondary: '#FFCDD2', // #FFCDD2
            accent: '#3F51B5', // #3F51B5
          },
        },
      }}),
      components:{
        
      },
    data: {
      kitchen_max_cleaners:null,
      new_kitchen_cabinet_productivity:null,
      old_kitchen_cabinet_productivity:null,
      new_kitchen_nocabinet_productivity:null,
      old_kitchen_nocabinet_productivity:null,
      absolute_cost:0,
      added_cost:0,
      addon_size:[],
      add_new_kitchen:true,
      addons_parsed:[],
      submit_loader:false,
      billingDataIndex:null,
      slot_msg:false,
      keynote_content:[
       'BEDROOMS','BATHROOMS','MAID ROOM','STORAGE ROOM','LIVING ROOM','DRESSING ROOM','CABINETS (Inside)','CABINETS (Outside)','DRIVER ROOM','LAUNDRY ROOM','MECHANICAL ROOM','ELECTRICAL ROOM','ENTERTAINMENT ROOM','DINING ROOM','ENTRANCE AREA','STAIR CASE','HAND WASH AREA','WINDOWS','WALL GLASS','BALCONY','SWIMMING POOL','FAÇADE','DUSTING','GATES & FENCE','HALL WAY','AC VENTS','COVE LIGHTS','SWITCH BOARDS','CHANDELIERS','WALL LIGHTS','CEILING LIGHTS','DOOR','ROOF TOP','FENCE','PARKING AREA'
      ],
      customDateSelected:[],
      customDialog:false,
      cleaningPolicy:'',
      altweekStat:false,
      subStat:'',
      altdaysStat:false,
      currentPageTitle:'Booking',
      custBookStat:false,
      scheduleStat:true,
      serviceChange:true,
        cat_counter:0,
        ser_counter:0,
      bookingMultiData:{},
  serviceImages:new FormData(),
  activePayment:'debit',
  imageUrl:'',
  imageObj:'',
  images:[],
   contact_platform:[],
  serviceDetails:{
    total_cost:0,
    estimated_cost:0,
    service_details:{},

  },
  tempCost:0,
  scale:80,
  quality:80,
  area_type:'',
  location_type:'',
  evaluator_note:'',
  multiServicesBill:[],
  refresh:0,
  floorCompleted:false,
  detailedCleaningServices:[],
  specialCareServices:[],
  buildingCount:1,
  kitchenCleaningServices:[],
  infectionControlServices:[],
    valid:[],
    validApartment:true,
    validKitchen:true,
    validKitchenDialog:true,
  
    validOtherService:true,
    validOtherServiceDialog:true,
    hallway_check:false,
    window_check:false,
    scheduleGroup:{},
   
    selectedCategory:'Detailed Cleaning',
  name: '',
  rules: {
    required: v => !!v || 'this field is required',
  },
  url:'',
   // url:'https://my.bleachkw.com',
    //url:'http://127.0.0.1:8000',
    slot_loader:false,
    kitchenData:{
        wall_type:'',
        floor_type:'',
        size:'',
        ceiling_type:'',
        condition:'',
        type:'old',
        residue:false,
        is_cabinet:false
    },
  mob_number: "",
  customerDetails: {},
  selectedAddress: {},
  today: "",
  otpStat: false,
  verifyStat: false,
  errorStat: false,
  errorVerifyStat: false,
  verificationStat: false,
  mob_otp: "",
  activeTab: "Services",
  selectedService: {
      name:'General Cleaning'
  },
  serviceSize: {},
  cartItems:[],
  selectedSlot: [],
  categories:['Detailed Cleaning','Special Care','Kitchen Cleaning','Infection Control'],
  area_types:[],
  location_types: [
    "Post Construction",
    "Post Renovation",
    "Fully Furnished",
    "Empty Area",
  ],
  services: [
    {
      name: "General Cleaning",
    },
    {
      name: "Deep Cleaning",
    },
    {
      name: "Upholstery Cleaning",
    },
    {
      name: "Carpet Cleaning",
    },
    {
      name: "Mattress Cleaning",
    },
    {
      name: "Kitchen Cleaning",
    },
    {
      name: "Sterilization",
    },
    {
      name: "Facade Cleaning",
    },
    {
      name: "Storage Area",
    },
    {
      name: "Car Parking Umbrella",
    },
    {
      name: "Window Cleaning",
    },
    {
      name: "Outdoor Cleaning",
    },
  ],
  currentServices:[
    {
        name: "General Cleaning",
      },
      {
        name: "Deep Cleaning",
      },
      
     
     
      {
        name: "Facade Cleaning",
      },
      {
        name: "Storage Area",
      },
      {
        name: "Car Parking Umbrella",
      },
      {
        name: "Window Cleaning",
      },
      {
        name: "Outdoor Cleaning",
      },
  ],
  buildingsCompleted: false,
  date: null,
  menu: false,
  ImageDetails: {
    url: "",
    file: "",
    service:""
  },
  dateSelected: "",
  userStat: true,
  images: [],
  duration: [],
  totalCost: 0,
  billingData: [],
  dialogStat: "",
  sizeData: [],
  currentItem: null,
  service: "test",
  dialog: false,
  dialogmsg: "",
  otherServices: [],
  otherService:{
    material: "",

    color: "",
    size: {},
    keynote_data:[],
    type: "",
    age: "",
    stain: false,
    stain_reason: "",
    wall_type: "",
    floor_type: "",
    ceiling_type: "",
    residue: false,
    hallway_size: "",
    sides: "",
    stain_age: "",
    height:"",
    is_cabinet:false,
    addons:[],
    section_net_cost:null,
    section_cost:null
  },
  color: ["Blue", "Yellow", "Orange", "Red", "Black", "White"],
  material: ["Material 1", "Material 2", "Material 3", "Material 4"],
  upholsteryType: ["SOFA", "CHAIR"],
  upholsterySize1: ["Small", "Medium", "Large", "Xtra Large"],
  upholsterySize2: ["Small", "Medium", "Large"],
  upholsterySize3: ["Small", "Medium", "Large"],
  tab: "tab1",
  e6: 1,
  e1: 1,
  serviceType: "",
  serviceTypes:[],
  apartment: [],
  no_of_apartments: [],

  e: {
    building: [],
  },
  no_of_building: 0,
  temp_no_of_building: 0,
  building: [],
  no_of_floors: [],
  buildings: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
  serviceSection: {
    service_type: "",
    area_type: "",
    location_type: "",
    sections: {},
  },
  area_types: [],
  

  location_types: [
    "Post Construction",
    "Post Renovation",
    "Fully Furnished",
    "Empty Area",
  ],
  location_types2:[
    "Fully Furnished",
    "Empty Area"
  ],
  splitData: ["8"],
  selectTest: "",
  selectedDuration: "8",
  size: ["SMALL", "MEDIUM", "LARGE"],
  cause_of_stain:['INK MARK', 'HARD DUST', 'COFFEE & TEA SPILL', 'OIL',
  'GREASE', 'PAINT', 'URINE', 'MILK SPILL', 'NO STAIN', 'OTHERS'],
  walltypes:["BRICKS","GLASS","CONCRETE","CERAMIC","GYPSUM","FABRIC","RUBBER","STONE","TERRAZO","STAINLESS","VINYL","WOODEN","OTHERS"],
  ceilingtypes:["WOODEN","GLASS","CONCRETE","CERAMIC","GYPSUM","FOAM","PLASTIC","FABRIC","RUBBER","STAINLESS","VENYL","OTHERS"],
  floortypes:["MARBLE","GLASS","STONE","CERAMIC","CONCRETE","BRICKS","WOODEN","TERRAZO","OTHERS"],
  materials:["POLYESTER","NATURAL FIBER","SYNTHETIC","LEATHER","OLEFIN","POLYPROPYLENE","NYLON"],
  colors:["GREEN","SILVER","VIOLET","WHITE","BLACK","BEIGE","BLUE","GREY","RED","CREAM","MULTI","OFF WHITE","MEROON","ORANGE","PINK","GOLD","BROWN","YELLOW","ROYAL BLUE","LILAC","OTHERS"],

  schedules: ["11", "15", "8", "23", "14"],
  imageData: [],
  dob:'',
  serviceData: {
    service_details: {
      service_type: "",
      location_type: "",
      area_type: "",
      evaluator_note: "",
      estimated_cost: 0,
      total_cost: 0,
      number_of_cleaners: 0,
      cleaning_hours: 0,
    },
    sections: {},
    customer_id: "",
    customer_details: {
      name: "",
      gender: "",
      email: "",
      mobile_number: "",
      dob: "",
      date_day: "",
      date_month: "",
      date_year: "",
      nationality: "",
      sms_preference: "",
      contact_platform: [],
    },
    address_id: "",
    address_details: {
      governorate: "",
      area: "",
      block: "",
      avenue: "",
      building: "",
      street: "",
      floor: "",
      apartment: "",
    },
  },
  sections: {
    section_name: "",
    size: "",
    wall_type: "",
    ceiling_type: "",
    cement_residue: false,
    section_cost: "",
    section_net_cost: "",
    keynotes: {},
  },
  upholsterySize: [],
  total_size: 0,
  slotDate: "",
  timeSlots: {},
  renderComponent: true,
  time_slot: {},
  slotCounter: 0,
  sizeFilteredData: [],
  kitchendialog:false,
  kitchenType:'',
  currentBuilding:'',
  currentFloor:'',
  currentKitchen:'',
  kitchendialogStat:false,
  kitchenSize:{},
  kitchenSizeData:[],
  facadeSize:[],
  windowSize:[],
  durationData:{},
  billSample:{
    name:'',
    section:{},
    section_name:'',
    serviceNo:1,
  },
  totalmanhour:0,
  maxCleaners:[],
  n:0,
  serviceCount:1,
  errMsg:'',
  kitchen_size:0,
  sofa_size:0,
  chair_size:0,
  caret_size:0,
  
  new_kitchen_cabinet_size:0,
  old_kitchen_cabinet_size:0,
  new_kitchen_nocabinet_size:0,
  old_kitchen_nocabinet_size:0,
  high_facade:0,
  low_facade:0,
  serviceTypesData:[],
  gateway_eval:'',
  gateway_price:0,
  cust_governorates:[],
  cust_areas:[],
  udf3:'',
  multiServiceImages:[],
  phase2Result:{},
  ip_address:'',
  owl_items:[],
prefDay:[],
scheduleDialog:false,
scheduleDate:'',
double_slots:[],
slotStat:{},
selected_double_slots:[],
visits:[],
visitDateTime:[],
no_of_visits:null,
monthly_starting_date:'',
menu2: false,
monthlyDialog:false,
week1:['01','02','03','04','05','06','07'],
week2:['08','09','10','11','12','13','14'],
week3:['15','16','17','18','19','20','21'],
week4:['22','23','24','25','26','27','28'],
week5:['29','30','31'],
autofixStat:false,
selected_monthly_date:[],
reselectDialog:false,
reselectSlot:[],
reselectDate:{},
reselectDateIndex:null,
scheduleFormat:{
  allSchedule:{},
  individual:{}
},

schedule_serviceTypes:[],
schedule_serviceTypes_selected:[],
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
  }
},
fixedSlots:{},
keynote_list:[],
keynote_data:{
  name:'',
  value:''
},    
keynote_name:'',
keynote_value:'',
scheduleDateSat:false,
confirmation_dialog:false,
schedule_err_msg:false,
onetime_dialog:false,
oneTimeDateSelected:'',
one_time_slots:{},
onetimerender:true,
selected_onetime_slots:{},
oneTimeSelectionStat:false,
onetime_scheduled:{},
togetherStat:false,
del_confirmation_dialog:false,
service_index:null,
editScheduleData:{},
editScheduleStat:false,
reconfirmation_dialog:false,
userid:'',
snackbar:false,
responseText:'',
parsedTimeSlots:[],
scheduleStatus:false,
floor_msg:false,
apartment_stat_err:false,
building_msg:false,
others_keynotes:[],
reset_building:false,
reset_floor:false,
building_warning:false,
available_slotes:[],
date_group:{},
addons:[],
last_image_stat:false,
hourly_cleaning:{
  duration:null,
  hourly_duration:null,
  cleaners:null
},
hourly_slots:true

      },
      methods: {
        findAddonCost(){
          var addon_cost=0
          for(var i=0;i<this.addons_parsed.length;i++){
            if(this.addons_parsed[i].selected){
              if(this.addons_parsed[i].details.category){
                addon_cost=addon_cost+(this.addons_parsed[i].selected_size.price*this.addons_parsed[i].quantity)
              }
              else{
                addon_cost=addon_cost+(this.addons_parsed[i].details.price*this.addons_parsed[i].quantity)
              }
            }
          }
          return addon_cost
        },
        findAbsoluteCost(){
          var total_cost = 0
          var addon_cost=0
          if(this.addons_parsed.length>0){
            for(var i=0;i<this.addons_parsed.length;i++){
              if(this.addons_parsed[i].selected){
                if(this.addons_parsed[i].details.category){
                  addon_cost=addon_cost+((this.addons_parsed[i].selected_size.price||0)*this.addons_parsed[i].quantity)
                }
                else{
                  addon_cost=addon_cost+((this.addons_parsed[i].details.price||0)*this.addons_parsed[i].quantity)
                }
              }
            }

          }
          
         total_cost=(this.otherService.size.cost||0)+addon_cost
         if(this.edit_item){
           total_cost=total_cost-this.billingData[this.currentItem].section_cost
         }
         if(total_cost)
         {
          console.log("absolute amount is "+total_cost)
         return total_cost
         }
         else{
           return 0
         }
        },
        closeEditDialog(){
          this.edit_item=false,
          this.otherService={
            material: "",
            addons:[],
            color: "",
            size: {},
            type: "",
            age: "",
            stain: false,
            stain_reason: "",
            wall_type: "",
            floor_type: "",
            ceiling_type: "",
            residue: false,
            is_cabinet:false,
            hallway_size: "",
            sides: "",
            stain_age: "",
            height:"",
            keynote_data:[],
            section_cost:0,
            sectiononly_cost:0
          },
          this.dialog=false
        },
        findAddedCost(){
          if(this.serviceType!='Hourly Cleaning')
          {
          var totalcost=0
         
          for(var i=0;i<this.billingData.length;i++){
           
            totalcost=totalcost+this.billingData[i].section_cost
          

          }
          if(totalcost){
            console.log("added amount is "+totalcost)
            return totalcost
          }
          else{
            console.log("added amount is "+totalcost)
            return 0
          }
        }
        else{
          return 0
        }
        },
        checkHourly(){
          for(var i=0;i<this.multiServicesBill.length;i++){
            if(this.multiServicesBill[i].service=='Hourly Cleaning'){
              return false
            }
           
          }
          return true
         
        },
        findFullAmount(){
          var fullamount=0
         
          for(var i=0;i<this.multiServicesBill.length;i++){
            var section_cost=0
            for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
              section_cost=section_cost+this.multiServicesBill[i].bill[j].section_cost
            }
            console.log("section cost"+i+" is "+section_cost)
            
            if(this.multiServicesBill[i].cleaning_policy=='SUBSCRIPTION' && this.multiServicesBill[i].schedule_details){
              if(Object.keys(this.multiServicesBill[i].schedule_details).length>0){
                fullamount=fullamount+(section_cost*(Object.keys(this.multiServicesBill[i].schedule_details).length))
              }
              else{
                fullamount=fullamount+section_cost
              }
            }
            else{
              fullamount=fullamount+section_cost
            }
          
          }
          console.log("full amount is "+fullamount)
          return fullamount
        },
        resetAllData(){
          this.reset_building=false
          this.building_warning=false
          this.no_of_building=this.temp_no_of_building
          this.valid=[]
    this.building=[]
    this.e.building=[]
    this.no_of_floors=[]
    this.reset_floor=false
    this.reset_building=false
    for (var i = 0; i < this.no_of_building; i++) {
      this.building.push({
        floors: [],
        completed:false
      });
      this.e.building.push({
        floors: [],
        e: 1,
      });
      this.no_of_floors.push("")
      this.valid.push({floors:[]})
    }
   
    this.reset_floor=true
    this.reset_building=true
        },
        cancelResetData(){
          this.temp_no_of_building=this.no_of_building
          this.building_warning=false
        },
        viewEditSchedule(service,index){
          this.schedule_serviceTypes_selected=[]
          this.editScheduleData=service
          this.editScheduleStat=true
          this.schedule_serviceTypes_selected.push(index)
         
          this.goToSchedule()
        },
        openDelConfirm(index){
          this.service_index=index
          this.del_confirmation_dialog=true
        },
        removeService(){
            this.multiServicesBill.splice(this.service_index,1)
            this.del_confirmation_dialog=false
        },
        oneTimeDateChange(){
          if(!this.one_time_slots[this.oneTimeDateSelected]){
            this.one_time_slots[this.oneTimeDateSelected]={
              slots:[]
            }
          }
          var yr=this.oneTimeDateSelected.split('-')[0]
          var mt=this.oneTimeDateSelected.split('-')[1]
          var dy=this.oneTimeDateSelected.split('-')[2]
          this.slotDate=dy+'-'+mt+'-'+yr
          this.getMultipleSlots()
          //this.calcSlots()
        },
        reconfirmScheduler(){
          this.reconfirmation_dialog=false
          for(var i=0;i<this.multiServicesBill.length;i++){
            this.multiServicesBill[i].schedule_details={}
          }
          this.resetScheduler()
          this.goToSchedule()
        },
        scheduleTogether()
        {
          if(this.serviceType=='Hourly Cleaning'){
            this.cleaningPolicy='Subscription'
          }
          if(this.checkScheduleAvail()){
            this.reconfirmation_dialog=true
          }
          else{
            this.goToSchedule()
          }
        },
        checkScheduleAvail(){
          var flag=false
          for(var i=0;i<this.multiServicesBill.length;i++){
            if(Object.keys(this.multiServicesBill[i].schedule_details).length>0){
              flag=true
              break
            }
            else{
              flag=false
            }
          }
          return flag
        },
        resetScheduler(){

          this.cleaningPolicy=''
          this.subStat=''
          this.visits=[]
          this.fixedSlots={}
          this.altdaysStat=false
          this.altweekStat=false
          this.selected_double_slots=[]
          this.selected_monthly_date=[]
          this.autofixStat=false
          this.selected_monthly_date=[]
          this.reselectDialog=false
          this.reselectSlot=[]
          this.reselectDate={}
          this.reselectDateIndex=null
         // this.one_time_slots={},

          this.selectedDuration={
            cleaners:null,
            hours:null,
            slots:null
          }
          this.scheduleFormat={
            allSchedule:{},
            individual:{}
          },
          this.no_of_visits='',
          this.scheduleDateSat=false
          this.confirmation_dialog=false
          this.monthly_starting_date=''
          this.customDateSelected=[]
          this.schedule_err_msg=false
          if(this.editScheduleStat){
            this.editScheduleStat=false
            this.editScheduleData.schedule_details={}
          }
          else{
            this.editScheduleData={}
          }
           this.oneTimeDateSelected=moment().format().split("T")[0];
            this.one_time_slots[this.oneTimeDateSelected]={
                slots:[]
            }

        },
        addKeynote(building,floor){
          if(this.keynote_name && this.keynote_value)
          {
          this.building[building].floors[floor].keynote_data.push({
            name:this.keynote_name,
            value:this.keynote_value
          })
          this.keynote_name=''
          this.keynote_value=''
        }
        },
        addOthersKeynote(){
          if(this.keynote_name && this.keynote_value)
          {
          this.otherService.keynote_data.push({
            name:this.keynote_name,
            value:this.keynote_value
          })
          this.keynote_name=''
          this.keynote_value=''
        }
        },
        removeOthersKeynote(keynote){
          this.otherService.keynote_data.splice(keynote,1)
      },
        removeKeynote(building,floor,keynote){
            this.building[building].floors[floor].keynote_data.splice(keynote,1)
        },
        addApartmentKeynote(building,floor,apartment){
          if(this.keynote_name && this.keynote_value)
          {
          this.building[building].floors[floor].apartments[apartment].keynote_data.push({
            name:this.keynote_name,
            value:this.keynote_value
          })
          this.keynote_name=''
          this.keynote_value=''
        }
        },
        removeApartmentKeynote(building,floor,apartment,keynote){
            this.building[building].floors[floor].apartments[apartment].keynote_data.splice(keynote,1)
        },
        calcSelectedServices(){
          this.schedule_serviceTypes=[]
          
            for(var i=0;i<this.schedule_serviceTypes_selected.length;i++){
              this.schedule_serviceTypes.push(this.multiServicesBill[this.schedule_serviceTypes_selected[i]].service)
              
                // if(this.checkKitchen(this.multiServicesBill[this.schedule_serviceTypes_selected[i]].bill)){
                //   this.schedule_serviceTypes.push('Kitchen Cleaning')

                // }
            }
          
        },
        checkKitchen(){
          for(var i=0;i<this.schedule_serviceTypes_selected.length;i++){
         
          var bills=this.multiServicesBill[this.schedule_serviceTypes_selected[i]].bill
          for(var j=0;j<bills.length;j++){
            if(bills[j].section.kitchen){
              return true
            }
          }
        }
          return false
        },
        addScheduledService(service,index){
          this.schedule_serviceTypes_selected[index]={
            service:service
          }
        },
        addOneTimeToSchedule(){
          if(this.scheduleStat){
            this.scheduleStatus=true
          }
          else{
            this.scheduleStatus=false
          }
          
            for(var j=0;j<this.schedule_serviceTypes_selected.length;j++){
              this.onetime_scheduled[this.schedule_serviceTypes_selected[j]]={
                slot:this.selected_onetime_slots
              }
            }
          
          for(var j=0;j<this.schedule_serviceTypes_selected.length;j++){
            this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaning_policy='ONE TIME SERVICE'
            this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details={}
            this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaners=this.selectedDuration.cleaners
           
            
            if(Object.keys(this.selected_onetime_slots).length>1){
              this.findContDate()
              var count=0
              for(var i in this.date_group){
                var cleaning_hr=0
                var dates=this.date_group[i]
                if(dates.length>0)
                {
                var min=dates[0]
                cleaning_hr=this.selected_onetime_slots[dates[0]].slots.length*2
                for(var m=1;m<dates.length;m++){
                    if(moment(dates[m],'YYYY-MM-DD').isBefore(moment(min,'YYYY-MM-DD'))){
                      
                      min=dates[m]
                    }
                
                    cleaning_hr=cleaning_hr+(this.selected_onetime_slots[dates[m]].slots.length*2)
                }
              
                /** add to schedule details */
                var yr=min.split('-')[0]
              var month=min.split('-')[1]
              var day=min.split('-')[2]
              var date=day+'-'+month+'-'+yr
              var min_slot=Math.min(...this.selected_onetime_slots[min].slots)
              this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[count+1]={
                
                "date":date,
               "time":this.slotFormat[parseInt(min_slot)].start_time,
              "no_of_cleaners":this.selectedDuration.cleaners,
               "cleaning_hours":cleaning_hr
              }
              count=count+1
              }
              }
            }
            else{

              var count=0
            for(var k in this.selected_onetime_slots){
              
              var yr=k.split('-')[0]
              var month=k.split('-')[1]
              var day=k.split('-')[2]
              var date=day+'-'+month+'-'+yr
              var min_slot=Math.min(...this.selected_onetime_slots[k].slots)
              this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[count+1]={
                
                "date":date,
               "time":this.slotFormat[parseInt(min_slot)].start_time,
              "no_of_cleaners":this.selectedDuration.cleaners,
               "cleaning_hours":this.selected_onetime_slots[k].slots.length*2
              }
              count=count+1
            }
          }

            //Find continous dates
          //   var removedDates=[]
          //   var contDates=[]
            
          //   for(var m in this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details){
          //   if (Object.keys(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details).length>1 && Object.keys(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details).length!=m){
            
          //     if(moment(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[m].date,'DD-MM-YYYY').add(1,'days').format('DD-MM-YYYY') == this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[(parseInt(m)+1)].date){
          //       if(contDates.includes())
          //       contDates.push(this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[m].date,this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[(parseInt(m)+1)].date)

          //     }
          //     else{
          //       console.log("yes i exited")
          //     }
          //   }
          // }
          }
          for(var k=0;k<this.schedule_serviceTypes_selected;k++)
          {
            for(var sch in this.scheduleGroup){
              // if(Array.isArray(this.scheduleGroup[sch])){
             if(this.scheduleGroup[sch].includes(this.schedule_serviceTypes_selected[k])){
               var index=this.scheduleGroup[sch].indexOf(this.schedule_serviceTypes_selected[k])
               console.log("index is"+index)
               this.scheduleGroup[sch].splice(index,1)
             }
              // }
             }
            }
          var groundid=Object.keys(this.scheduleGroup).length
          this.scheduleGroup[groundid]=[ ...this.schedule_serviceTypes_selected ]
          this.selected_onetime_slots={}

          this.onetime_scheduled={}
          this.oneTimeSelectionStat=false
          this.schedule_serviceTypes_selected=[]
         this.oneTimeDateSelected=this.today
         this.dateSelected=this.today
         this.formatDate()
         this.one_time_slots={}
          this.activeTab='Cart'
        },
        findContDate(){
          
          var dates=Object.keys(this.selected_onetime_slots)
          var count=0;
          var found=false
          this.date_group[count]=[]
          for(var i=0;i<dates.length;i++){
            found=false
              if(dates.includes(moment(dates[i],'YYYY-MM-DD').add(1,'days').format('YYYY-MM-DD'))){
                
                for(var g in this.date_group){
                  if(this.date_group[g].includes(dates[i])){
                    found=true;
                    break;
                  }
                }
                if(!found){
                  
                  if(this.selected_onetime_slots[dates[i]].slots.includes("12") && this.selected_onetime_slots[moment(dates[i],'YYYY-MM-DD').add(1,'days').format('YYYY-MM-DD')].slots.includes("1"))
                  {
                    if(this.date_group[count].length>0){
                      if((this.date_group[count].includes(this.selected_onetime_slots[moment(dates[i],'YYYY-MM-DD').add(1,'days').format('YYYY-MM-DD')]))||(this.date_group[count].includes(this.selected_onetime_slots[moment(dates[i],'YYYY-MM-DD').subtract(1,'days').format('YYYY-MM-DD')])))
                      {

                      this.date_group[count].push(dates[i])
                      }
                      else{
                        count=count+1
                        this.date_group[count].push(dates[i])
                      }

                    }
                    else{
                      this.date_group[count].push(dates[i])
                    }
                  for(var g in this.date_group){
                    if(this.date_group[g].includes(moment(dates[i],'YYYY-MM-DD').add(1,'days').format('YYYY-MM-DD'))){
                      found=true;
                      break;
                    }
                  }
                  if(!found){
                   
                    this.date_group[count].push(moment(dates[i],'YYYY-MM-DD').add(1,'days').format('YYYY-MM-DD'))
                  }
                 
                  }
                  else{
                    found=false
                    count=count+1
                    
                    this.date_group[count]=[]
                    for(var g in this.date_group){
                      if(this.date_group[g].includes(dates[i])){
                        found=true;
                        break;
                      }
                    }
                    if(!found){
                     
                    this.date_group[count].push(dates[i])
                    }
                  }
                }
                  
              }
              else{
                found=false
                count=count+1
                
                this.date_group[count]=[]
                for(var g in this.date_group){
                  if(this.date_group[g].includes(dates[i])){
                    found=true;
                    break;
                  }
                }
                if(!found){
                 
                this.date_group[count].push(dates[i])
                }
              }
              
          }
        },
        addAllServiceTypes(){
          this.schedule_serviceTypes_selected=[]
          if(this.scheduleStat){
            for(var i=0;i<this.multiServicesBill.length;i++){
              this.schedule_serviceTypes_selected.push(i)
            }
          }
          else{
            this.schedule_serviceTypes_selected=[]
          }
          this.calcSelectedServices()
        },
        addToSchedule(){
          
          if(this.scheduleStat){
            this.scheduleStatus=true
          }
          else{
            this.scheduleStatus=false
          }
            for(var i=0;i<this.schedule_serviceTypes_selected.length;i++){
              
              this.scheduleFormat.individual[this.schedule_serviceTypes_selected[i]]={
                starting_date:this.visits[0].dateTime,
                visits:this.visits
              }
              
            }
          var cleaners=this.selectedDuration.cleaners
          for(var j=0;j<this.schedule_serviceTypes_selected.length;j++){
            this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaning_policy='SUBSCRIPTION'
            this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details={}
            this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaners=cleaners
            for(var k=0;k<this.visits.length;k++){
              var min_slot=Math.min(...this.visits[k].slots)
              
              this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[k+1]={
                
                "date":this.visits[k].date,
               "time":this.slotFormat[min_slot].start_time,
              "no_of_cleaners":this.selectedDuration.cleaners,
               "cleaning_hours":this.selectedDuration.hours
              }
            }
           
          }
          for(var k=0;k<this.schedule_serviceTypes_selected;k++)
          {
            for(var sch in this.scheduleGroup){
              // if(Array.isArray(this.scheduleGroup[sch])){
             if(this.scheduleGroup[sch].includes(this.schedule_serviceTypes_selected[k])){
               var index=this.scheduleGroup[sch].indexOf(this.schedule_serviceTypes_selected[k])
               console.log("index is"+index)
               this.scheduleGroup[sch].splice(1,index)
             }
            // }
             }
            }
          var groundid=Object.keys(this.scheduleGroup).length
          this.scheduleGroup[groundid]=[ ...this.schedule_serviceTypes_selected ]

          this.visits=[]
          this.selected_double_slots=[]
         this.selectedDuration={
            cleaners:'',
            hours:'',
            slots:''
          }
          this.fixedSlots={}
          this.reselectDateIndex=null
          this.reselectDate={}
          this.subStat='',
          cleaningPolicy='',
          no_of_visits='',
          this.visits=[]
          this.schedule_serviceTypes_selected=[]
          this.scheduleDateSat=false
          this.activeTab='Cart'
        },
        changeVisitDate(){
          this.slot_msg=false
        if(this.selected_double_slots.length==this.selectedDuration.hours/2)
        {
          var day=moment(this.dateSelected,'YYYY-MM-DD') 
            var dayname=day.format('ddd')
            var startSlot=Math.min(...this.selected_double_slots)
            var dateTime=day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
            this.visits[this.reselectDateIndex]={
              date:day.format('DD-MM-YYYY'),      
              slots:this.selected_double_slots,
              day:dayname,
              dateTime:day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
            }
            this.visitDateTime=[]
            this.visitDateTime.push(dateTime)
            this.fixedSlots={}
            this.checkAvailablility()
            this.reselectDialog=false
            this.slot_msg=false
          }
          else{
            this.slot_msg=true
          }
        },
        reselectVisitDate(slot,index){
          this.reselectDate=slot
          this.reselectDateIndex=index
          this.reselectDialog=true
          this.selected_double_slots=[]
        },
        selectMonthlyDate(date){
          if(this.selected_monthly_date.includes(date)){
            var index=this.selected_monthly_date.indexOf(date)
            this.selected_monthly_date.splice(index,1)
          }
          else{
            this.selected_monthly_date.push(date)
          }
          
          
        },
        checkFixedSlots(slot,index){
          console.log("fixed slot is "+this.fixedSlots[slot])
          var duration=this.visits[index].slots.length*2
          console.log("duration : "+duration)
          var startTime=''
          var end=''
          var endTime=''
          var totalTime=''
          if(this.fixedSlots[slot]!='Not Available' && this.fixedSlots[slot] ){
           // console.log("found the slot")
           this.visits[index].slots=[]
            var start=this.fixedSlots[slot]
             console.log("start is"+start)
             startTime=moment(start,'DD-MM-YYYY hh:mm A').format('hh:mm A')
             end=moment(start,'DD-MM-YYYY hh:mm A').add(duration,'hours')
             endTime=moment(end).format('hh:mm A')
             totalTime=startTime+' - '+endTime
             console.log("START time is"+moment(start)+'end time :'+end)
            console.log("fixed time is"+totalTime)
           
            this.visits[index].status='fixed'
           this.visits[index].dateTime=slot.split(' ')[0]+' '+startTime
            
            var counter=startTime
            var limit=endTime
            console.log("counter"+counter+'limit :'+limit)
            while(moment(counter,'hh:mm A').isBefore(moment(limit,'hh:mm A')))
            {
            for(var i in this.slotFormat){
              console.log("slot format:"+this.slotFormat[i].start_time+'counter :'+counter)
              if(this.slotFormat[i].start_time==counter){
                this.visits[index].slots.push(parseInt(i))
              }
            }
            counter=moment(counter,'hh:mm A').add(2,'hours').format('hh:mm A')
            
          }
          return totalTime
        }
          else{
            return false
          }
          
        },
        getCombinedSlot(slots){
          var min=Math.min(...slots)
          var max=Math.max(...slots)
          console.log("aray:"+slots+"min is"+min+"max is"+max)
          var combined = this.slotFormat[String(min)].start_time+' - '+this.slotFormat[String(max)].end_time
          return combined
        },
        getCombinedOnetimeSlot(slots){
          var min=Math.min(...slots)
          var max=Math.max(...slots)
          console.log("aray:"+slots+"min is"+min+"max is"+max)
          var combined = this.slotFormat[parseInt(min)].start_time+' - '+this.slotFormat[parseInt(max)].end_time
          return combined
        },
        findCustomVisits(){
          if(this.serviceType=='Hourly Cleaning'){
            this.findHourlyCost()
          }
          if(this.selected_double_slots.length==this.selectedDuration.hours/2){

          
          if(this.customDateSelected.length>0 && this.selected_double_slots.length>0 )
          {
         for(var i=0;i<this.customDateSelected.length;i++){
           var day=moment(this.customDateSelected[i],'YYYY-MM-DD')
           var dayname=day.format('ddd')
           var startSlot=Math.min(...this.selected_double_slots)
           var dateTime=day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
           this.visits.push({
            date:day.format('DD-MM-YYYY'),      
            slots:this.selected_double_slots,
            day:dayname,
            dateTime:day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
          })
          
           this.visitDateTime.push(dateTime)
         }
         this.checkAvailablility()
         this.customDialog=false
         this.scheduleDateSat=true
         this.schedule_err_msg=false
        }
        else{
          this.schedule_err_msg=true
        }
        this.slot_msg=false
      }
      else{
        this.slot_msg=true
      }

          
        },
        findVisits(){
          if(this.serviceType=='Hourly Cleaning'){
            this.findHourlyCost()
          }
          if(this.selected_double_slots.length==this.selectedDuration.hours/2){
        if(this.selected_double_slots.length>0 && this.dateSelected)
        {
         this.scheduleDialog=false

         /* Weekly Cleaning calculator */
         if(this.subStat=='Weekly')
         {
         var count=0
        var visitcount=0

          while(count<999){
            
            var day=moment(this.dateSelected,'YYYY-MM-DD').add(count,"days")
            
            var dayname=day.format('ddd')
            var startSlot=Math.min(...this.selected_double_slots)
            var dateTime=day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
            if(this.prefDay.includes(dayname)){
              this.visits.push({
                date:day.format('DD-MM-YYYY'),      
                slots:this.selected_double_slots,
                day:dayname,
                dateTime:day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
              })
              
               this.visitDateTime.push(dateTime)
              visitcount++
           
            }
            if(visitcount==parseInt(this.no_of_visits)){
              this.checkAvailablility()
              break;
            }
            if(this.altweekStat && dayname=='Sat'){
              count=count+8
            }
           else{
            count++
           }
          }   
          }  
          /* Daily Cleaning calculator */
          else if(this.subStat=='Daily')
         {
          var count=0
          var visitcount=0
          while(count<999){
            
            var day=moment(this.dateSelected,'YYYY-MM-DD').add(count,"days")
            
          
            var startSlot=Math.min(...this.selected_double_slots)
            var dateTime=day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
            
              this.visits.push({
                date:day.format('DD-MM-YYYY'),      
                slots:this.selected_double_slots,
              
                dateTime:day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
              })
              
               this.visitDateTime.push(dateTime)
              visitcount++
           
            
            if(visitcount==parseInt(this.no_of_visits)){
              this.checkAvailablility()
              break;
            }
            if(this.altdaysStat){
              count=count+2
            }
           else{
            count++
           }
          } 
         }
         this.scheduleDateSat=true
        }
        else{
          this.schedule_err_msg=true
        }
        this.slot_msg=false
      }
      else{
        this.slot_msg=true
      }
        },
        findHourlyCost(){
          var total_cost=7.5*parseInt(this.hourly_cleaning.cleaners)*parseInt(this.hourly_cleaning.hourly_duration)

          this.multiServicesBill[0].bill[0].section_net_cost=total_cost
          this.multiServicesBill[0].bill[0].section_cost=total_cost
          this.multiServicesBill[0].bill[0].section.section_net_cost=total_cost
          this.multiServicesBill[0].bill[0].section.section_cost=total_cost
          this.multiServicesBill[0].bill[0].sectiononly_cost=total_cost
          this.multiServicesBill[0].bill[0].sectiononly_net_cost=total_cost
          this.multiServicesBill[0].total_cost=total_cost
        },
        findMonthlyVisits(){
          if(this.serviceType=='Hourly Cleaning'){
            this.findHourlyCost()
          }
          if(this.selected_double_slots.length==this.selectedDuration.hours/2){
          if(this.selected_monthly_date.length>0 && this.selected_double_slots.length>0 )
          {
        
          var count=0
          var visitcount=0
          while(count<999){
            
            var day=moment(this.monthly_starting_date,'YYYY-MM-DD').add(count,"days")
          
           var dayNo=day.format('DD')
           console.log("dayno"+dayNo)
           if(dayNo!=undefined)
           {
           if(this.selected_monthly_date.includes(String(dayNo)))
           {
          
            var startSlot=Math.min(...this.selected_double_slots)
            var dateTime=day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
            
              this.visits.push({
                date:day.format('DD-MM-YYYY'),      
                slots:this.selected_double_slots,
              
                dateTime:day.format('DD-MM-YYYY')+' '+this.slotFormat[startSlot].start_time
              })
              
               this.visitDateTime.push(dateTime)
               visitcount++
            }
          }
              
           
            
            if(visitcount==parseInt(this.no_of_visits)){
             this.checkAvailablility()
              break;
            }
           
            
           
            count++
           
          }
          this.monthlyDialog=false 
          this.scheduleDateSat=true
        }
        else{
          this.schedule_err_msg=true
        }
        this.slot_msg=false
      }
      else{
        this.slot_msg=true
      }
        },
        checkAvailablility(){
          var schedule_serviceTypes=this.schedule_serviceTypes
          if(this.serviceType=='Hourly Cleaning'){
            schedule_serviceTypes=[]
            schedule_serviceTypes.push('General Cleaning')
          }
         axios.post(this.url+'/customer/ajax/multipleservice/multipledates/cleaningslotes/',{number_of_cleaners:this.selectedDuration.cleaners,
          cleaning_hours:this.selectedDuration.hours,
          service_types:schedule_serviceTypes,
          cleaning_datetimes:this.visitDateTime}).then(response=>{
            this.slotStat=response.data
            for(var i=0;i<this.visits.length;i++){
              if(this.slotStat.available_slotes.includes(this.visits[i].dateTime)){
                this.visits[i].status='fixed'
              }
            }
            if(this.slotStat.busy_slotes.length>0){
              this.autofixStat=false
            }
            else{
              this.autofixStat=true
            }

         })
          
          
        },
        autoFix(){
          this.fixedSlots={}
          axios.post(this.url+'/customer/ajax/multipleservice/multipledates/cleaningslotes/autofix/',{number_of_cleaners:this.selectedDuration.cleaners,
           cleaning_hours:this.selectedDuration.hours,
           service_types:this.schedule_serviceTypes,
           cleaning_datetimes:this.slotStat.busy_slotes}).then(response=>{
             this.fixedSlots=response.data.slote_details
             this.autofixStat=true
             
 
          })
           
           
         },
         checkFixStatus(){
           var flag=false
          for(var i=0;i<this.visits.length;i++){
            if(this.visits[i].status){
              if(this.visits[i].status=='fixed'){
                flag=true
              }
              else{
                flag=false
                break
              }
            }
            else{
              flag=false
              break
            }
          }
          return flag
         },
        calcSlots(){
          this.double_slots=[]
          this.selected_double_slots=[]
          var slot={
            "0":[2,4,6,8,10,12,14,16,18,20,22,24],
            "2":[2,4,6,8,10,12,14,16,18,20,22,24],
            "4":[2,4,6,8,10,12,14,16,18,20,22,24],
            "6":[2,4,6,8,10,12,14,16,18,20,22,24],
            "8":[2,4,6,8,10,12,14,16,18,20,22,24],
            "10":[2,4,6,8,10,12,14,16,18,20,22,24],
            "12":[2,4,6,8,10,12,14,16,18,20,22,24],
            "14":[2,4,6,8,10,12,14,16,18,20,22,24],
            "16":[2,4,6,8,10,12,14,16,18,20,22,24],
            "18":[2,4,6,8,10,12,14,16,18,20,22,24],
            "20":[2,4,6,8,10,12,14,16,18,20,22,24],
            "22":[2,4,6,8,10,12,14,16,18,20,22,24]
    
          }
          for(var i in slot){
            if(slot[i].includes(2)){
              var slotNo=(parseInt(i)+2)/2
    
              this.double_slots.push(this.slotFormat[String(slotNo)])
              
              
            }
          }
     },
 /*calcSlots(){
      var slot={
        "0":[2,4,6,8,10,12,14,16,18,20,22,24],
        "2":[2,4,6,8,10,12,14,16,18,20,22,24],
        "4":[2,4,6,8,10,12,14,16,18,20,22,24],
        "6":[2,4,6,8,10,12,14,16,18,20,22,24],
        "8":[2,4,6,8,10,12,14,16,18,20,22,24],
        "10":[2,4,6,8,10,12,14,16,18,20,22,24],
        "12":[2,4,6,8,10,12,14,16,18,20,22,24],
        "14":[2,4,6,8,10,12,14,16,18,20,22,24],
        "16":[2,4,6,8,10,12,14,16,18,20,22,24],
        "18":[2,4,6,8,10,12,14,16,18,20,22,24],
        "20":[2,4,6,8,10,12,14,16,18,20,22,24],
        "22":[2,4,6,8,10,12,14,16,18,20,22,24]

      }
      for(var i in slot){
        if(slot[i].includes(2)){
          if(i<12){
            startTime=i+'AM'
          }
          else{
            startTimeUnit='PM'
          }
          var endTime=i+2
          if(endTime<12){
            sTimeUnit='AM'
          }
          else{
            startTimeUnit='PM'
          }
          
          var startSlot=parseInt(i)+12
          this.double_slots.push({
            slotNo:i,
            slot:
          })
        }
      }
 },*/
     selectPrefDay(day){
       if(!this.prefDay.includes(day))
       {
      this.prefDay.push(day)
       }
       else{
        const prefIndex = this.prefDay.indexOf(day);
         this.prefDay.splice(prefIndex,1)
       }
     },
  getIp(){
    axios.get('https://www.cloudflare.com/cdn-cgi/trace').then((response)=>{

      response.data = response.data.trim().split('\n').reduce(function(obj, pair) {
  pair = pair.split('=');
  return obj[pair[0]] = pair[1], obj;
}, {});
console.log(response)
      this.ip_address=response.data.ip
    })
  },
  uploadFile(){
    this.$refs.item-image.input.click()
    console.log("ref is "+ this.$refs.imageComp)
  },
  goToPayment(){
    if(this.activePayment=='debit'){
      this.$refs.gateway_submit.click()
    }
    if(this.activePayment=='credit'){
      //this.$refs.gateway_credit_submit.click()
      //console.log("url: "+ "https://testpay.bleach-kw.com/creditcard/payment_form.php?merchant_defined_data1="+this.bookingMultiData.order_details.order_no+"&reference_number="+this.bookingMultiData.order_details.order_no+"&merchant_defined_data2=prepaid&amount="+this.bookingMultiData.order_details.total_amount+"&currency=KWD&transaction_type=sale&bill_to_forename="+this.bookingMultiData.customer_details.customer.name.split(' ')[1]+"&bill_to_surname="+this.bookingMultiData.customer_details.customer.name.split(' ')[2]+"&bill_to_phone=mobile"+this.bookingMultiData.customer_details.customer.mobile_number+"&bill_to_email="+this.bookingMultiData.customer_details.customer.email+"&bill_to_address_country="+this.bookingMultiData.customer_details.customer.nationality+"&bill_to_address_city="+this.bookingMultiData.cleaning_details[0].address.area.name+"&bill_to_address_line1="+this.bookingMultiData.cleaning_details[0].address.governorate.name+"&merchant_defined_data4="+this.bookingMultiData.customer_details.payment_method+"&merchant_defined_data5=NO&merchant_defined_data7=1&merchant_defined_data20=NO&customer_ip_address="+this.ip_address )
      window.location.href="https://testpay.bleach-kw.com/creditcard/payment_form.php?merchant_defined_data1="+this.bookingMultiData.order_details.order_no+"&reference_number="+this.bookingMultiData.order_details.order_no+"&merchant_defined_data2=prepaid&amount="+this.bookingMultiData.order_details.total_amount+"&currency=KWD&transaction_type=sale&bill_to_forename="+this.bookingMultiData.customer_details.customer.name.split(' ')[1]+"&bill_to_surname="+this.bookingMultiData.customer_details.customer.name.split(' ')[2]+"&bill_to_phone=mobile"+this.bookingMultiData.customer_details.customer.mobile_number+"&bill_to_email="+this.bookingMultiData.customer_details.customer.email+"&bill_to_address_country="+this.bookingMultiData.customer_details.customer.nationality+"&bill_to_address_city="+this.bookingMultiData.cleaning_details[0].address.area.name+"&bill_to_address_line1="+this.bookingMultiData.cleaning_details[0].address.governorate.name+"&merchant_defined_data4="+this.bookingMultiData.customer_details.payment_method+"&merchant_defined_data5=NO&merchant_defined_data7=1&merchant_defined_data20=NO&customer_ip_address="+this.ip_address
    }
  },
  selectPayment(pay){
    console.log("pay is "+pay)
    this.activePayment=pay
    console.log("pay is "+this.activePayment)
  },
   getFiles(obj){
     this.scale=60
     this.quality=60
      console.log(obj)
      this.imageObj=obj
     
      if(obj.compressed){
       this.images.push(obj)
        this.imageURL = URL.createObjectURL(obj.compressed.file)
      }
      
    },
 
    getServices(){
      axios
      .get(
        this.url+"/customer/ajax/getservicetypes"
      )
      .then((response) => {
          this.serviceTypesData=response.data.service_types
      })
    },
    getGovernorate(){
      axios
      .get(
        this.url+"/customer/ajax/getgovernorates"
      )
      .then((response) => {
          this.cust_governorates=response.data.governorates
      })
    },
     getAreas(){
       console.log("governorate is "+this.serviceDetails.address_details.governorate)
       var governorate=this.serviceDetails.address_details.governorate
      axios
      .get(
        this.url+"/customer/ajax/getareas?governorate_id="+governorate
      )
      .then((response) => {
          this.cust_areas=response.data.areas
      })
    },
    getServiceId(service){
      
      for(var i=0;i<this.serviceTypesData.length;i++){
        if(this.serviceTypesData[i].name==service){
          console.log("i found")
          return this.serviceTypesData[i].id
        }
      }
    },
    scheduleBooking(){
      this.activeTab='Address'
        var count=0
        for(var i in this.time_slot){
          
          for(var j=0;j<this.time_slot[i].selectedSlot.length;j++)
          {
             if(this.time_slot[i].selectedSlot[j]==0){
              var selectedTime='12:00 am'
            }
            else if(this.time_slot[i].selectedSlot[j]<12){
              var selectedTime=this.time_slot[i].selectedSlot[j]+':00 am'
            }
            else if(this.time_slot[i].selectedSlot[j]>12){
              var selectedTime=(parseInt(this.time_slot[i].selectedSlot[j])-12)+':00 pm'
            }
            else{
             var  selectedTime='12:00 pm'
            }
              count=count+1
               this.serviceDetails.schedule_details[count]={
               date:i,
               time:selectedTime,
               cleaning_hours:this.selectedDuration.hours,
               no_of_cleaners:this.selectedDuration.cleaners
               
          }
          }
         
        }
       
        
    },
    checkScheduleStatus(){
      var flag=false
      for(var i=0;i<this.multiServicesBill.length;i++){
        if(Object.keys(this.multiServicesBill[i].schedule_details).length<1){
          flag=false
          break
        }
        else{
          flag=true
        }
      }
      return flag
    },
    arrangeData(){
          for(var i=0;i<this.multiServicesBill.length;i++){

            var service_id=this.getServiceId(this.multiServicesBill[i].service)
             this.serviceDetails.service_details[i]={
                "service_type":service_id,
                "cleaning_policy":this.multiServicesBill[i].cleaning_policy,
                "schedule_details":this.multiServicesBill[i].schedule_details,
                "location_type":this.multiServicesBill[i].location_type,
                "area_type":this.multiServicesBill[i].area_type,
                 "evaluator_note":this.multiServicesBill[i].evaluator_note,
                 "estimated_cost":this.multiServicesBill[i].total_cost,
                 "total_cost":this.multiServicesBill[i].total_cost,
                 "number_of_cleaners":this.multiServicesBill[i].cleaners,
                   "cleaning_hours":parseInt(this.selectedDuration.hours),
                   sections:{}
              }
              if(this.serviceDetails.service_details[i].cleaning_policy=='SUBSCRIPTION'){
                var visits=Object.keys(this.multiServicesBill[i].schedule_details).length
                this.serviceDetails.service_details[i].total_cost=parseInt(this.serviceDetails.service_details[i].total_cost)*parseInt(visits)
                this.serviceDetails.service_details[i].estimated_cost=parseInt(this.serviceDetails.service_details[i].total_cost)
              }
            for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
              this.serviceDetails.service_details[i].sections[j]={
                "section_name":this.multiServicesBill[i].bill[j].section_name,
              "size":this.multiServicesBill[i].bill[j].section.size.name,
              "wall_type":"",
              "floor_type":'',
              "ceiling_type":'',
              "cement_residue":this.multiServicesBill[i].bill[j].section.cement_residue,
              "oil_residue":this.multiServicesBill[i].bill[j].section.residue,
              "section_cost":this.multiServicesBill[i].bill[j].section_cost,
              "sectiononly_cost":this.multiServicesBill[i].bill[j].sectiononly_cost,
              "sectiononly_net_cost":this.multiServicesBill[i].bill[j].sectiononly_cost,
              "section_net_cost":this.multiServicesBill[i].bill[j].section_net_cost,
              "keynotes":{},
              "addons":{},
              "new_kitchen":false,
              "is_cabinet":false,
              "is_highprice_facade":false,
              "is_highprice_window":false,
              "colour":'',
              "material":'',
              "cause_of_stain":'',
              "upholstery_type":'',
              "age":'',
              "age_of_stain":''
              
              }
              if(this.serviceDetails.service_details[i].cleaning_policy=='SUBSCRIPTION'){
                this.serviceDetails.service_details[i].sections[j].sectiononly_net_cost=this.serviceDetails.service_details[i].sections[j].sectiononly_net_cost*parseInt(visits)
                this.serviceDetails.service_details[i].sections[j].section_net_cost=this.serviceDetails.service_details[i].sections[j].section_net_cost*parseInt(visits)
              }
              if(this.multiServicesBill[i].bill[j].section.size.is_highprice_facade){
                this.serviceDetails.service_details[i].sections[j].is_highprice_facade=true
              }
              
              if(this.multiServicesBill[i].bill[j].section.size.is_highprice_window){
                this.serviceDetails.service_details[i].sections[j].is_highprice_window=true
              }
              if(this.multiServicesBill[i].bill[j].section.size.is_newkitchen){
                this.serviceDetails.service_details[i].sections[j].new_kitchen=true
              }
              if(this.multiServicesBill[i].bill[j].section.is_cabinet){
                this.serviceDetails.service_details[i].sections[j].is_cabinet=true
              }
              if(this.multiServicesBill[i].bill[j].section.stain_age){
                this.serviceDetails.service_details[i].sections[j].age_of_stain=this.multiServicesBill[i].bill[j].section.stain_age
              }
              if(this.multiServicesBill[i].bill[j].section.color){
                this.serviceDetails.service_details[i].sections[j].colour=this.multiServicesBill[i].bill[j].section.color.join()
              }
              if(this.multiServicesBill[i].bill[j].section.material){
                this.serviceDetails.service_details[i].sections[j].material=this.multiServicesBill[i].bill[j].section.material.join()
              }
              if(this.multiServicesBill[i].bill[j].section.stain_reason){
                this.serviceDetails.service_details[i].sections[j].cause_of_stain=this.multiServicesBill[i].bill[j].section.stain_reason
              }
              if(this.multiServicesBill[i].bill[j].section.type=='SOFA'||this.multiServicesBill[i].bill[j].section.type=='CHAIR')
           {
             this.serviceDetails.service_details[i].sections[j].upholstery_type=this.multiServicesBill[i].bill[j].section.type
           
           }
           if(this.multiServicesBill[i].bill[j].section.wall_type)
           {
             this.serviceDetails.service_details[i].sections[j].wall_type=this.multiServicesBill[i].bill[j].section.wall_type.join()
           
           }
           if(this.multiServicesBill[i].bill[j].section.ceiling_type)
           {
             this.serviceDetails.service_details[i].sections[j].ceiling_type=this.multiServicesBill[i].bill[j].section.ceiling_type.join()
           
           }
           if(this.multiServicesBill[i].bill[j].section.floor_type)
           {
             this.serviceDetails.service_details[i].sections[j].floor_type=this.multiServicesBill[i].bill[j].section.floor_type.join()
           
           }
           if(this.multiServicesBill[i].bill[j].section.age)
           {
             this.serviceDetails.service_details[i].sections[j].age=this.multiServicesBill[i].bill[j].section.age
           
           }
          
           var keynotecounter=1
           if(this.multiServicesBill[i].bill[j].section.no_of_bathrooms){
            this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
              "sub_area":"bathroom",
              "quantity":this.multiServicesBill[i].bill[j].section.no_of_bathrooms

            }
            keynotecounter=keynotecounter+1
           }
           if(this.multiServicesBill[i].bill[j].section.no_of_rooms){
            this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
              "sub_area":"rooms",
              "quantity":this.multiServicesBill[i].bill[j].section.no_of_rooms

            }
            keynotecounter=keynotecounter+1
           }
           if(this.multiServicesBill[i].bill[j].section.no_of_windows){
            this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
              "sub_area":"windows",
              "quantity":this.multiServicesBill[i].bill[j].section.no_of_windows

            }
            keynotecounter=keynotecounter+1
           }
         
           if(this.multiServicesBill[i].bill[j].section.keynote_data.length>0){
             
             for(var ky=0;ky<this.multiServicesBill[i].bill[j].section.keynote_data.length;ky++){
              this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
                "sub_area":this.multiServicesBill[i].bill[j].section.keynote_data[ky].name,
                "quantity":this.multiServicesBill[i].bill[j].section.keynote_data[ky].value
  
              }
              keynotecounter=keynotecounter+1
             }

           }
           var addoncounter=0
           if(this.multiServicesBill[i].bill[j].section.addons){
            
             for(add_on=0;add_on<this.multiServicesBill[i].bill[j].section.addons.length;add_on++){
             
               if(this.multiServicesBill[i].bill[j].section.addons[add_on].selected)
               {
                addoncounter=addoncounter+1
              this.serviceDetails.service_details[i].sections[j].addons[addoncounter]={
                name:this.multiServicesBill[i].bill[j].section.addons[add_on].details.name,
                addon_cost:this.multiServicesBill[i].bill[j].section.addons[add_on].details.price,
                addon_net_cost:this.multiServicesBill[i].bill[j].section.addons[add_on].details.price*this.multiServicesBill[i].bill[j].section.addons[add_on].quantity,
                quantity:this.multiServicesBill[i].bill[j].section.addons[add_on].quantity,
                size:'',
                other_details:''
              }
              if(this.multiServicesBill[i].bill[j].section.addons[add_on].details.category){
                this.serviceDetails.service_details[i].sections[j].addons[addoncounter].size=this.multiServicesBill[i].bill[j].section.addons[add_on].selected_size.size
              }
            }
             }
           }
           if(this.multiServicesBill[i].bill[j].section.kitchen){
            var newindex=Object.keys(this.serviceDetails.service_details[i].sections[j].addons).length
            for(var k=0;k<this.multiServicesBill[i].bill[j].section.kitchens.length;k++){
              newindex=newindex+1
              this.serviceDetails.service_details[i].sections[j].addons[newindex]={
                name:"kitchen",
                addon_cost:this.multiServicesBill[i].bill[j].section.kitchens[k].size.cost,
                addon_net_cost:this.multiServicesBill[i].bill[j].section.kitchens[k].size.cost,
                quantity:1,
                size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.name,
                other_details:JSON.stringify({
                  size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.name,
                  max_size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.max_size,
                  type:this.multiServicesBill[i].bill[j].section.kitchens[k].type,
                  residue:this.multiServicesBill[i].bill[j].section.kitchens[k].residue,
                  is_cabinet:this.multiServicesBill[i].bill[j].section.kitchens[k].is_cabinet
                })
              }
            }

           }
          /* if(this.multiServicesBill[i].bill[j].section.kitchen){
            var newindex=Object.keys(this.serviceDetails.service_details[i].sections[j].keynotes).length
            var kitchencounter=newindex
            for(var k=0;k<this.multiServicesBill[i].bill[j].section.kitchens.length;k++){
             this.serviceDetails.service_details[i].sections[j].keynotes[kitchencounter]={
               "sub_area":'kitchen',
               "quantity":JSON.stringify({
                 size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.name,
                 max_size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.max_size,
                 type:this.multiServicesBill[i].bill[j].section.kitchens[k].type,
                 residue:this.multiServicesBill[i].bill[j].section.kitchens[k].residue,
                 cost:this.multiServicesBill[i].bill[j].section.kitchens[k].size.cost
               })
               
             
             }
             kitchencounter=kitchencounter+1
             keynotecounter=keynotecounter+1
            }
           
          }*/
            }
          }
          var tc=0
        for(var sr in this.serviceDetails.service_details )
        {
          tc=tc+parseInt(this.serviceDetails.service_details[sr].total_cost)
        }
          this.serviceDetails.total_cost=tc
          this.serviceDetails.estimated_cost=tc
        
          this.bookMultipleService()
    },
    arrangeCustData(){
      for(var i=0;i<this.multiServicesBill.length;i++){

        var service_id=this.getServiceId(this.multiServicesBill[i].service)
         this.serviceDetails.service_details[i]={
            "service_type":service_id,
            "location_type":this.multiServicesBill[i].location_type,
            "area_type":this.multiServicesBill[i].area_type,
             "evaluator_note":this.multiServicesBill[i].evaluator_note,
             "estimated_cost":this.multiServicesBill[i].total_cost,
             "total_cost":this.multiServicesBill[i].total_cost,
               sections:{}
          }
          for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
            this.serviceDetails.service_details[i].sections[j]={
              "section_name":this.multiServicesBill[i].bill[j].section_name,
            
            "size":this.multiServicesBill[i].bill[j].section.size.name,
            "wall_type":"",
            "floor_type":'',
            "ceiling_type":'',
            "cement_residue":this.multiServicesBill[i].bill[j].section.cement_residue,
            "oil_residue":this.multiServicesBill[i].bill[j].section.residue,
            "section_cost":this.multiServicesBill[i].bill[j].section_net_cost,
            "sectiononly_cost":this.multiServicesBill[i].bill[j].sectiononly_cost,
            "sectiononly_net_cost":this.multiServicesBill[i].bill[j].sectiononly_cost,
            "section_net_cost":this.multiServicesBill[i].bill[j].section_net_cost,
            "keynotes":{},
            "addons":{},
            "new_kitchen":false,
            "is_cabinet":false,
            "is_highprice_facade":false,
            "is_highprice_window":false,
            "colour":'',
            "material":'',
            "cause_of_stain":'',
            "upholstery_type":'',
            "age":''
            
            }
          
            if(this.multiServicesBill[i].bill[j].section.size.is_highprice_facade){
              this.serviceDetails.service_details[i].sections[j].is_highprice_facade=true
            }
            if(this.multiServicesBill[i].bill[j].section.size.is_highprice_window){
              this.serviceDetails.service_details[i].sections[j].is_highprice_window=true
            }
            if(this.multiServicesBill[i].bill[j].section.size.is_newkitchen){
              this.serviceDetails.service_details[i].sections[j].new_kitchen=true
            }
            if(this.multiServicesBill[i].bill[j].section.is_cabinet){
              this.serviceDetails.service_details[i].sections[j].is_cabinet=true
            }
            if(this.multiServicesBill[i].bill[j].section.stain_age){
              this.serviceDetails.service_details[i].sections[j].age_of_stain=this.multiServicesBill[i].bill[j].section.stain_age
            }
            if(this.multiServicesBill[i].bill[j].section.color){
              this.serviceDetails.service_details[i].sections[j].colour=this.multiServicesBill[i].bill[j].section.color.join()
            }
            if(this.multiServicesBill[i].bill[j].section.material){
              this.serviceDetails.service_details[i].sections[j].material=this.multiServicesBill[i].bill[j].section.material.join()
            }
            if(this.multiServicesBill[i].bill[j].section.stain_reason){
              this.serviceDetails.service_details[i].sections[j].cause_of_stain=this.multiServicesBill[i].bill[j].section.stain_reason
            }
            if(this.multiServicesBill[i].bill[j].section.type=='SOFA'||this.multiServicesBill[i].bill[j].section.type=='CHAIR')
         {
           this.serviceDetails.service_details[i].sections[j].upholstery_type=this.multiServicesBill[i].bill[j].section.type
         
         }
         if(this.multiServicesBill[i].bill[j].section.wall_type)
         {
           this.serviceDetails.service_details[i].sections[j].wall_type=this.multiServicesBill[i].bill[j].section.wall_type.join()
         
         }
         if(this.multiServicesBill[i].bill[j].section.ceiling_type)
         {
           this.serviceDetails.service_details[i].sections[j].ceiling_type=this.multiServicesBill[i].bill[j].section.ceiling_type.join()
         
         }
         if(this.multiServicesBill[i].bill[j].section.floor_type)
         {
           this.serviceDetails.service_details[i].sections[j].floor_type=this.multiServicesBill[i].bill[j].section.floor_type.join()
         
         }
         if(this.multiServicesBill[i].bill[j].section.age)
         {
           this.serviceDetails.service_details[i].sections[j].age=this.multiServicesBill[i].bill[j].section.age
         
         }
        
         var keynotecounter=1
         if(this.multiServicesBill[i].bill[j].section.no_of_bathrooms){
          this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
            "sub_area":"bathroom",
            "quantity":this.multiServicesBill[i].bill[j].section.no_of_bathrooms

          }
          keynotecounter=keynotecounter+1
         }
         if(this.multiServicesBill[i].bill[j].section.no_of_rooms){
          this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
            "sub_area":"rooms",
            "quantity":this.multiServicesBill[i].bill[j].section.no_of_rooms

          }
          keynotecounter=keynotecounter+1
         }
         if(this.multiServicesBill[i].bill[j].section.no_of_windows){
          this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
            "sub_area":"windows",
            "quantity":this.multiServicesBill[i].bill[j].section.no_of_windows

          }
          keynotecounter=keynotecounter+1
         }
         if(this.multiServicesBill[i].bill[j].section.keynote_data.length>0){
           for(var ky=0;ky<this.multiServicesBill[i].bill[j].section.keynote_data.length;ky++){
            this.serviceDetails.service_details[i].sections[j].keynotes[keynotecounter]={
              "sub_area":this.multiServicesBill[i].bill[j].section.keynote_data[ky].name,
              "quantity":this.multiServicesBill[i].bill[j].section.keynote_data[ky].value

            }
            keynotecounter=keynotecounter+1
           }

         }
         var addoncounter=0
           if(this.multiServicesBill[i].bill[j].section.addons){
            
             for(add_on=0;add_on<this.multiServicesBill[i].bill[j].section.addons.length;add_on++){
             
               if(this.multiServicesBill[i].bill[j].section.addons[add_on].selected)
               {
                addoncounter=addoncounter+1
              this.serviceDetails.service_details[i].sections[j].addons[addoncounter]={
                name:this.multiServicesBill[i].bill[j].section.addons[add_on].details.name,
                addon_cost:this.multiServicesBill[i].bill[j].section.addons[add_on].details.price,
                addon_net_cost:this.multiServicesBill[i].bill[j].section.addons[add_on].details.price*this.multiServicesBill[i].bill[j].section.addons[add_on].quantity,
                quantity:this.multiServicesBill[i].bill[j].section.addons[add_on].quantity
              }
              if(this.multiServicesBill[i].bill[j].section.addons[add_on].details.category){
                this.serviceDetails.service_details[i].sections[j].addons[addoncounter].size=this.multiServicesBill[i].bill[j].section.addons[add_on].selected_size.size
              }
            }
             }
           }
           if(this.multiServicesBill[i].bill[j].section.kitchen){
            var newindex=Object.keys(this.serviceDetails.service_details[i].sections[j].addons).length
            for(var k=0;k<this.multiServicesBill[i].bill[j].section.kitchens.length;k++){
              newindex=newindex+1
              this.serviceDetails.service_details[i].sections[j].addons[newindex]={
                name:"kitchen",
                addon_cost:this.multiServicesBill[i].bill[j].section.kitchens[k].size.cost,
                addon_net_cost:this.multiServicesBill[i].bill[j].section.kitchens[k].size.cost,
                quantity:1,
                size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.name,
                other_details:JSON.stringify({
                  size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.name,
                  max_size:this.multiServicesBill[i].bill[j].section.kitchens[k].size.max_size,
                  type:this.multiServicesBill[i].bill[j].section.kitchens[k].type,
                  residue:this.multiServicesBill[i].bill[j].section.kitchens[k].residue,
                  is_cabinet:this.multiServicesBill[i].bill[j].section.kitchens[k].is_cabinet
                  
                })
              }
            }

           }
          }
      }
   
      this.serviceDetails.total_cost=this.totalCost
      this.serviceDetails.estimated_cost=this.totalCost
    
      this.bookCustService()
    },
    openFloor(index,floor){
      this.e.building[index - 1].e = floor
      this.building[index - 1].completed=false
    },
    openApartment(index,floor,apindex){
      this.e.building[index - 1].floors[floor - 1].e = apindex + 1
      this.building[index-1].floors[floor-1].completed=false
    },
    addKitchen(building,floor){
      
        if(this.$refs['kitchenFloor-building-'+(building)+'floor-'+(floor)][0].validate())
     { 
        console.log("kitchen data is  "+JSON.stringify(this.kitchenData))
        this.building[building].floors[floor].kitchens.push(this.kitchenData)
          this.forceRerender();
          this.kitchenData={
        wall_type:'',
        floor_type:'',
        size:'',
        ceiling_type:'',
        condition:'',
        is_cabinet:false,
        type:'old',
        residue:false
    }
   this.recalcPrice(building,floor)
     }
       
    },
    addApartmentKitchen(building,floor,apartment){
      
       
        console.log("kitchen data is  "+JSON.stringify(this.kitchenData))
        this.building[building].floors[floor].apartments[apartment].kitchens.push(this.kitchenData)
          this.forceRerender();
          this.kitchenData={
        wall_type:'',
        floor_type:'',
        size:'',
        ceiling_type:'',
        condition:'',
        is_cabinet:false,
        type:'old',
        residue:false
    }
   this.recalcApartmentPrice(building,floor,apartment)
 
       
    },
      addMoreKitchen(building,floor){
      
        if(this.$refs['KitchenForm-building-'+building+'floor'-floor].validate())
     { 
        console.log("kitchen data is  "+JSON.stringify(this.kitchenData))
        var temp = { ...this.kitchenData }
        this.building[building].floors[floor].kitchens.push(temp)
          this.forceRerender();
          this.kitchenData={
        wall_type:'',
        floor_type:'',
        size:'',
        ceiling_type:'',
        condition:'',
        type:'old',
        residue:false
    }
    this.kitchendialog=false
    this.recalcPrice(building,floor)
       
    }
      },
      changeFloorKitchenStat(building,floor){
        if(!this.building[building].floors[floor].kitchen){
          this.building[building].floors[floor].kitchens=[]
        }
        this.recalcPrice(building,floor)
      },
      changeApartmentKitchenStat(building,floor,apartment){
        if(!this.building[building].floors[floor].apartments[apartment].kitchen){
          this.building[building].floors[floor].apartments[apartment].kitchens=[]
        }
        this.recalcApartmentPrice(building,floor,apartment)
      },
    addMoreKitchenApartment(building,floor,apartment){
      
       
        console.log("kitchen data is  "+JSON.stringify(this.kitchenData))
        var temp = { ...this.kitchenData }
        this.building[building].floors[floor].apartments[apartment].kitchens.push(temp)
          this.forceRerender();
          this.kitchenData={
        wall_type:'',
        floor_type:'',
        size:'',
        ceiling_type:'',
        condition:'',
        residue:false,
        type:'old'
    }
    this.kitchendialog=false
    this.recalcApartmentPrice(building,floor,apartment)
       
    },
      addNewKitchen(building,floor){
      
        this.kitchenType='floor'
       this.currentBuilding=building
       this.currentFloor=floor
        this.kitchendialog=true
        this.kitchendialogStat=true
        this.kitchenData={
          wall_type:'',
          floor_type:'',
          size:'',
          ceiling_type:'',
          condition:'',
          type:'old',
          residue:false
      }
        
       
       
    },
    addNewKitchenWithAddon(){
      this.otherService = {
        material: "",
        color: "",
        size: "",
        type: "old",
        age: "",
        stain: false,
        stain_reason: "",
        wall_type: "",
        floor_type: "",
        ceiling_type: "",
        residue: false,
        hallway_size: "",
        sides: "",
        stain_age: "",
        height:"",
        keynote_data:[],
        addons:[]
      }
      this.add_new_kitchen=true
      this.currentItem=null
      this.parseAddons()
    },
    addNewApartmentKitchen(building,floor,apartment){
      
       this.kitchenType='apartment'
       this.currentBuilding=building
       this.currentFloor=floor
       this.currentApartment=apartment
        this.kitchendialog=true
        this.kitchendialogStat=true
        this.kitchenData={
          wall_type:'',
          floor_type:'',
          size:'',
          ceiling_type:'',
          condition:'',
          type:'old',
          residue:false
      }
       
    },
     editNewKitchen(building,floor,serv){
      
       this.kitchenType='floor'
       this.currentBuilding=building
       this.currentFloor=floor
       this.currentKitchen=serv
        this.kitchendialog=true
        this.kitchendialogStat=false
        this.kitchenData.wall_type=this.building[building].floors[floor].kitchens[serv].wall_type
         this.kitchenData.floor_type=this.building[building].floors[floor].kitchens[serv].floor_type
          this.kitchenData.size=this.building[building].floors[floor].kitchens[serv].size
           this.kitchenData.ceiling_type=this.building[building].floors[floor].kitchens[serv].ceiling_type
        this.kitchenData.condition=this.building[building].floors[floor].kitchens[serv].condition
        this.kitchenData.type=this.building[building].floors[floor].kitchens[serv].type
        this.kitchenData.residue=this.building[building].floors[floor].kitchens[serv].residue

      
       
    },
      editNewApartmentKitchen(building,floor,apartment,serv){
      
       this.kitchenType='apartment'
       this.currentBuilding=building
       this.currentFloor=floor
       this.currentKitchen=serv
        this.currentApartment=apartment
        this.kitchendialog=true
        this.kitchendialogStat=false
        this.kitchenData.wall_type=this.building[building].floors[floor].apartments[apartment].kitchens[serv].wall_type
         this.kitchenData.floor_type=this.building[building].floors[floor].apartments[apartment].kitchens[serv].floor_type
          this.kitchenData.size=this.building[building].floors[floor].apartments[apartment].kitchens[serv].size
           this.kitchenData.ceiling_type=this.building[building].floors[floor].apartments[apartment].kitchens[serv].ceiling_type
        this.kitchenData.condition=this.building[building].floors[floor].apartments[apartment].kitchens[serv].condition
        this.kitchenData.type=this.building[building].floors[floor].apartments[apartment].kitchens[serv].type
        this.kitchenData.residue=this.building[building].floors[floor].apartments[apartment].kitchens[serv].residue
      
       
    },
    updateKitchen(){
        this.building[this.currentBuilding].floors[this.currentFloor].kitchens[this.currentKitchen]=this.kitchenData
        this.kitchendialog=false
        this.forceRerender()
        this.kitchenData={
        wall_type:'',
        floor_type:'',
        size:'',
        ceiling_type:'',
        condition:'',
        type:'',
        residue:false
    }
    this.recalcPrice(this.currentBuilding,this.currentFloor)
    },
      updateKitchenApartment(){
        this.building[this.currentBuilding].floors[this.currentFloor].apartments[this.currentApartment].kitchens[this.currentKitchen]=this.kitchenData
        this.kitchendialog=false
        this.forceRerender()
        this.kitchenData={
        wall_type:'',
        floor_type:'',
        size:'',
        ceiling_type:'',
        condition:'',
        type:'old',
        residue:false
    }
    this.recalcApartmentPrice(this.currentBuilding,this.currentFloor,this.currentApartment)
    },
    deleteKitchen(building,floor,service){
        console.log("called me..buildin is "+building+"floor is "+floor+"service is"+service)
        this.building[building].floors[floor].kitchens.splice(service,1)
        this.forceRerender();
         this.recalcPrice(building,floor);
    },
     deleteApartmentKitchen(building,floor,apartment,service){
        console.log("called me..buildin is "+building+"floor is "+floor+"service is"+service)
        this.building[building].floors[floor].apartments[apartment].kitchens.splice(service,1)
        this.forceRerender();
         this.recalcApartmentPrice(building,floor,apartment);
    },
  changeKitchen() {
    

    this.sizeFilteredData = [];
    this.otherService.size=""
    if (this.otherService.type == "new") {
      this.parseAddons()
      $('.more-services').hide()
      if(this.otherService.is_cabinet)
      {
      console.log("type test passed new");
      for (var i = 0; i < this.sizeData.length; i++) {
        if (this.sizeData[i].is_newkitchen && this.sizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.sizeData[i]);
        }
      }
    }
    else{
      for (var i = 0; i < this.sizeData.length; i++) {
        if (this.sizeData[i].is_newkitchen && !this.sizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.sizeData[i]);
        }
      }
    }
    }
    if (this.otherService.type == "old") {
      $('.more-services').show()
      if(this.otherService.is_cabinet)
      {
      console.log("type test passed old");
      for (var i = 0; i < this.sizeData.length; i++) {
        if (!this.sizeData[i].is_newkitchen && this.sizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.sizeData[i]);
        }
      }
    }
    else{
      for (var i = 0; i < this.sizeData.length; i++) {
        if (!this.sizeData[i].is_newkitchen && !this.sizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.sizeData[i]);
        }
      }
    }
    }
  },
  changeNewKitchen(){
    this.kitchenData.size=''
      axios
      .get(
        this.url+"/customer/ajax/getservicesizeprice?service_type=Kitchen Cleaning"
      )
      .then((response) => {
        this.kitchenSize = response.data;
        this.kitchenSizeData = [];
    console.log("servuc size is " + this.kitchenSize);
    for (var i in this.kitchenSize) {
      this.kitchenSize[i]["combinedSize"] =
        this.kitchenSize[i].name +
        " ( " +
        this.kitchenSize[i].min_size +
        " sq. m - " +
        this.kitchenSize[i].max_size +
        " sq. m )";
      this.kitchenSizeData.push(this.kitchenSize[i]);
    }
    this.serviceSize = {};
         if (this.kitchenData.type == "new") {
          $('.more-services').hide()
          this.parseAddons()
          if(this.kitchenData.is_cabinet)

          {
      console.log("type test passed new");
      for (var i = 0; i < this.kitchenSizeData.length; i++) {
        if (this.kitchenSizeData[i].is_newkitchen && this.kitchenSizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.kitchenSizeData[i]);
        }
      }
    }
    else{
      for (var i = 0; i < this.kitchenSizeData.length; i++) {
        if (this.kitchenSizeData[i].is_newkitchen && !this.kitchenSizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.kitchenSizeData[i]);
        }
      }
    }
    }
    if (this.kitchenData.type == "old") {
      $('.more-services').show()
      console.log("type test passed old");
      if(this.kitchenData.is_cabinet)
      {
      for (var i = 0; i < this.kitchenSizeData.length; i++) {
        if (!this.kitchenSizeData[i].is_newkitchen && this.kitchenSizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.kitchenSizeData[i]);
        }
      }
    }
    else{
      for (var i = 0; i < this.kitchenSizeData.length; i++) {
        if (!this.kitchenSizeData[i].is_newkitchen && !this.kitchenSizeData[i].is_cabinet) {
          this.sizeFilteredData.push(this.kitchenSizeData[i]);
        }
      }
    }
    }
      })
      .catch((error) => {
        console.log(error);
      });
       this.sizeFilteredData = [];
   
  },
  sendOtp() {
    axios
      .get( this.url+"/customer/ajax/addressotpsend?mobile_number=" + this.mob_number
       
      )
      .then((response) => {
        this.otpStat = true;
        this.errorStat = false;
        if (!response.data.success) {
          this.errorStat = true;
          this.otpStat = false;
        }
      })
      .catch((error) => {
        console.log(error);
        this.errorStat = true;
      });
  },
  verifyOtp() {
    axios
      .get( this.url+"/customer/ajax/addressotpverify?address_otp=" + this.mob_otp
        
      )
      .then((response) => {
        this.verifyStat = true;
        this.errorVerifyStat = false;
        if (!response.data.success) {
          this.errorVerifyStat = true;
          this.verifyStat = false;
        } else {
          this.verificationStat = true;
          this.customerDetails = response.data;
          this.selectedAddress=this.customerDetails.customer_addresses[0]
        }
      })
      .catch((error) => {
        console.log(error);
        this.verifyStat = false;
        this.errorVerifyStat = false;
      });
  },
    verifyTest() {
    axios
      .get( this.url+"/customer/ajax/addressotpverifytest?mobile_number=" + this.mob_number       
      )
      .then((response) => {
        this.verifyStat = true;
        this.errorVerifyStat = false;
        if (!response.data.success) {
          this.errorVerifyStat = true;
          this.verifyStat = false;
        } else {
          this.verificationStat = true;
          this.customerDetails = response.data;
          this.selectedAddress=this.customerDetails.customer_addresses[0]
        }
      })
      .catch((error) => {
        console.log(error);
        this.verifyStat = false;
        this.errorVerifyStat = false;
      });
  },
  checkSlot(slot) {
    if (
      this.slotCounter < this.selectedDuration.slots &&
      this.time_slot[this.slotDate].selectedSlot.length < 4
    ) {
      if (this.time_slot[this.slotDate].selectedSlot.length > 0) {
        var nextSlot = parseInt(slot) + 3;
        var prevSlot = parseInt(slot) - 3;
        var stat = false;
        console.log("next slot is" + nextSlot);
        console.log("prev slot is" + prevSlot);
        for (
          var i = 0;
          i < this.time_slot[this.slotDate].selectedSlot.length;
          i++
        ) {
          if (
            this.time_slot[this.slotDate].selectedSlot[i] == nextSlot ||
            this.time_slot[this.slotDate].selectedSlot[i] == prevSlot
          ) {
            stat = true;
          }
        }
        return stat;
      } else {
        return true;
      }
    } else {
      return false;
    }
  },
  forceRerender() {
    // Remove my-component from the DOM
    this.renderComponent = false;

    this.$nextTick(() => {
      // Add the component back in
      this.renderComponent = true;
    });
  },
  addDoubleSlot(start,end,slot){
      this.selected_double_slots.push(slot)
  },
  addOneTimeSlot(start,end,slot){
   this.onetimerender=false
  var currSlot=''
   for(var i in this.slotFormat){
     if(this.slotFormat[i].start_time==start){
      currSlot=i
      break;
     }
   }
    this.one_time_slots[this.oneTimeDateSelected].slots.push(currSlot)
    this.onetimerender=true
},
resetOneTime(){
  this.onetimerender=false
  this.one_time_slots={}
  this.date_group={}
  this.one_time_slots[this.oneTimeDateSelected]={
    slots:[]
  }
 
  this.onetimerender=true
},
checkSlotSelection(){
  for(var i in  this.one_time_slots){
    if(this.one_time_slots[i].slots.length>0){
      return true
    
    }
    
  }
  return false
},
checkOneTimeSlot(start,end,slot){
  
  var currSlot=''
   for(var i in this.slotFormat){
     if(this.slotFormat[i].start_time==start){
      currSlot=i
      break;
     }
   }
   if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(currSlot)){
     return true
   }
   else{
     return false
   }
  
},
removeOneTimeSlot(slot){
  this.onetimerender=false
  var prevSlot=parseInt(slot)-1
  var nextSlot=parseInt(slot)+1
  var index=this.one_time_slots[this.oneTimeDateSelected].slots.indexOf(slot)
  this.one_time_slots[this.oneTimeDateSelected].slots.splice(index,1)
  if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(nextSlot)&&this.one_time_slots[this.oneTimeDateSelected].slots.includes(prevSlot))
  {
    var tempSlots=[...this.one_time_slots[this.oneTimeDateSelected].slots]
    for(var i=0;i<this.one_time_slots[this.oneTimeDateSelected].slots.length;i++){
      if(this.one_time_slots[this.oneTimeDateSelected].slots[i]>slot){
        var slotindex=tempSlots.indexOf(this.one_time_slots[this.oneTimeDateSelected].slots[i])
        tempSlots.splice(slotindex,1)
      }
    }
    console.log("duble slot is "+this.selected_double_slots+"tempslot:"+tempSlots)
    this.one_time_slots[this.oneTimeDateSelected].slots=[...tempSlots]

  }
  this.onetimerender=true
},

  removeDoubleSlot(slot){
    var prevSlot=parseInt(slot)-1
    var nextSlot=parseInt(slot)+1
    var index=this.selected_double_slots.indexOf(slot)
    this.selected_double_slots.splice(index,1)
    if(this.selected_double_slots.includes(nextSlot)&&this.selected_double_slots.includes(prevSlot))
    {
      var tempSlots=[...this.selected_double_slots]
      for(var i=0;i<this.selected_double_slots.length;i++){
        if(this.selected_double_slots[i]>slot){
          var slotindex=tempSlots.indexOf(this.selected_double_slots[i])
          tempSlots.splice(slotindex,1)
        }
      }
      console.log("duble slot is "+this.selected_double_slots+"tempslot:"+tempSlots)
      this.selected_double_slots=[...tempSlots]
    }
  },
  checkSlotStat(slot){
    
    var prevSlot=parseInt(slot)-1
    var nextSlot=parseInt(slot)+1
    if(this.selected_double_slots.length<this.selectedDuration.slots)
    {
    if(this.selected_double_slots.length>0)
    {
    if(slot==1){
      if(this.selected_double_slots.includes(nextSlot)){
        return true
      }
      else {
        return false
      }
    }
    else if(slot==12){
      if(this.selected_double_slots.includes(prevSlot)){
        return true
      }
      else {
        return false
      }
    }
    else{
      if(this.selected_double_slots.includes(prevSlot)||this.selected_double_slots.includes(nextSlot))
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
  }
  else{
    return false
  }
  },
  
  checkOneTimeSlotStat(start,end,slot){
    for(var i in this.slotFormat){
      if(this.slotFormat[i].start_time==start){
       currSlot=i
       break;
      }
    }
   
    var prevSlot=parseInt(currSlot)-1
    var nextSlot=parseInt(currSlot)+1
   
    var counter=0
    for(var i in this.one_time_slots){
      counter=counter+this.one_time_slots[i].slots.length
    }
    if(counter<this.selectedDuration.slots)
    {
      
    if(this.one_time_slots[this.oneTimeDateSelected].slots.length>0)
    {
     
    if(slot==1){
      if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(String(nextSlot))){
        return true
      }
      else {
        return false
      }
    }
    else if(slot==12){
      if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(String(prevSlot))){
        return true
      }
      else {
        return false
      }
    }
    else{
    
      if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(String(prevSlot))||this.one_time_slots[this.oneTimeDateSelected].slots.includes(String(nextSlot)))
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
  }
  else{
    return false
  }
  },

  oneTimeSlotCounter(){
    var counter=0
    for(var i in this.one_time_slots){
      counter=counter+this.one_time_slots[i].slots.length
    }
    return counter
  },
  submitOneTimeSlots(){
    this.slot_msg=false
    var slotscount=this.oneTimeSlotCounter()
    var slots_required=this.selectedDuration.hours/2
    if(slotscount==slots_required)
    {
    this.selected_onetime_slots={}
    
      for(var i in this.one_time_slots){
        if(this.one_time_slots[i].slots.length>0){
          this.selected_onetime_slots[i]={
            slots:this.one_time_slots[i].slots
          }
        }
      }
    
  
  
    this.onetime_dialog=false
    this.oneTimeSelectionStat=true
    }
    else{
      this.slot_msg=true
    }
  },
  
  addSlot(slot) {
    if (this.time_slot[this.slotDate].selectedSlot.length == 0) {
      this.time_slot[this.slotDate].selectedSlot.push(slot);
      this.forceRerender();
      this.countSlots();
    } else {
      var nextSlot = slot + 3;
      if (this.time_slot[this.slotDate].selectedSlot.includes(nextSlot)) {
        if (this.timeSlots[slot].includes(6)) {
          this.time_slot[this.slotDate].selectedSlot.push(slot);
          this.forceRerender();
          this.countSlots();
        } else {
          console.log("slot cannot be selected");
        }
      } else {
        if (slot > 0) {
          var prevSlot = slot - 3;
          if (this.timeSlots[prevSlot].includes(6)) {
            this.time_slot[this.slotDate].selectedSlot.push(slot);
            this.forceRerender();
            this.countSlots();
          } else {
            console.log("slot cannot be selected");
          }
        }
      }
      //var slotStart=this.time_slot[this.slotDate].selectedSlot[0]
    }
  },
  countSlots() {
    this.slotCounter = 0;
    for (var slot in this.time_slot) {
      this.slotCounter =
        parseInt(this.slotCounter) +
        parseInt(this.time_slot[slot].selectedSlot.length);
    }
  },
  removeSlot(slot) {
    this.time_slot[this.slotDate].selectedSlot.splice(
      this.time_slot[this.slotDate].selectedSlot.indexOf(slot),
      this.time_slot[this.slotDate].selectedSlot.length
    );
    this.countSlots();
    this.forceRerender();
  },
  updateSize() {
    console.log("updatin size");
    this.upholsterySize = [];
    for (var i = 0; i < this.sizeData.length; i++) {
      if (this.sizeData[i].upholstery_type == this.otherService.type) {
        this.upholsterySize.push(this.sizeData[i]);
        console.log("updated size");
      }
    }
  },
  findSelectedTotalSize() {
    this.total_size = 0
    this.sofa_size=0
    this.chair_size=0
    console.log("called me & "+this.schedule_serviceTypes_selected)
    for(var j=0;j<this.schedule_serviceTypes_selected.length;j++)
    {
      console.log("i m inside loop")
        var serIndex=this.schedule_serviceTypes_selected[j]
       if(this.multiServicesBill[serIndex].service=='Upholstery Cleaning'){
        console.log("i m inside upholsdtery")
         for (var i=0;i < this.multiServicesBill[serIndex].bill.length; i++) {
                if(this.multiServicesBill[serIndex].bill[i].section.type=='SOFA'){
                  this.sofa_size=this.sofa_size+ parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size)
                }
                if(this.multiServicesBill[serIndex].bill[i].section.type=='CHAIR'){
                  this.chair_size=this.chair_size+ parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size)
                }
          }
       }
       else if(this.multiServicesBill[serIndex].service=='Kitchen Cleaning'){
        console.log("i m inside kitchen")
         for (var i=0;i < this.multiServicesBill[serIndex].bill.length; i++) {
                if(this.multiServicesBill[serIndex].bill[i].section.type=='old'){
                  if(this.multiServicesBill[serIndex].bill[i].is_cabinet){
                    this.old_kitchen_cabinet_size=this.old_kitchen_cabinet_size+ parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size)
                  }
                  else{
                    this.old_kitchen_nocabinet_size=this.old_kitchen_nocabinet_size+ parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size)
                  }
                  
                }
                if(this.multiServicesBill[serIndex].bill[i].section.type=='new'){
                  if(this.multiServicesBill[serIndex].bill[i].is_cabinet){
                    this.new_kitchen_cabinet_size=this.new_kitchen_cabinet_size+ parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size)
                  }
                  else{
                  this.new_kitchen_nocabinet_size=this.new_kitchen_nocabinet_size+ parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size)
                }
              }
          }
       }
       else if(this.multiServicesBill[serIndex].service=='Kitchen Appliances')
       {

       }
       else{

       console.log("i m inside")
    for (var i=0;i < this.multiServicesBill[serIndex].bill.length; i++) {
      if(this.multiServicesBill[serIndex].bill[i].section.size)
      {
     console.log("section sixze is"+this.multiServicesBill[serIndex].bill[i].section.size.max_size)
      this.total_size=this.total_size + parseInt(this.multiServicesBill[serIndex].bill[i].section.size.max_size);
      console.log("section total sixze is"+this.total_size)
      }
    }
    }
    }
    console.log("total size is "+this.total_size)
  },
  findTotalSize() {
    this.total_size = 0
    this.sofa_size=0
    this.chair_size=0
    for(var j=0;j<this.multiServicesBill.length;j++)
    {
       if(this.multiServicesBill[j].service=='Upholstery Cleaning'){
         for (var i=0;i < this.multiServicesBill[j].bill.length; i++) {
                if(this.multiServicesBill[j].bill[i].section.type=='SOFA'){
                  this.sofa_size=this.sofa_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
                }
                if(this.multiServicesBill[j].bill[i].section.type=='CHAIR'){
                  this.chair_size=this.chair_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
                }
          }
       }
       else if(this.multiServicesBill[j].service=='Kitchen Cleaning'){
        for (var i=0;i < this.multiServicesBill[j].bill.length; i++) {
          if(this.multiServicesBill[j].bill[i].section.type=='old'){
            if(this.multiServicesBill[j].bill[i].is_cabinet){
              this.old_kitchen_cabinet_size=this.old_kitchen_cabinet_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
            }
            else{
              this.old_kitchen_nocabinet_size=this.old_kitchen_nocabinet_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
            }
            
          }
          if(this.multiServicesBill[j].bill[i].section.type=='new'){
            if(this.multiServicesBill[j].bill[i].is_cabinet){
              this.new_kitchen_cabinet_size=this.new_kitchen_cabinet_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
            }
            else{
            this.new_kitchen_nocabinet_size=this.new_kitchen_nocabinet_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
          }
        }
    }
       }
       else{

       
    for (var i=0;i < this.multiServicesBill[j].bill.length; i++) {
     
      this.total_size=this.total_size + parseInt(this.multiServicesBill[j].bill[i].section.size.max_size);
    }
    }
    }
    console.log("total size is "+this.total_size)
  },
  selectService(service) {
    this.serviceChange=false
    this.selectedService = service;
    this.serviceType = service.name;
    this.location_type=''
    this.area_type=''
    this.otherServices = [];
   this.billingData=[];
    this.building = [];
    this.no_of_building = 0;
    this.temp_no_of_building = 0;
    this.no_of_floors = [];
    this.no_of_apartments = [];
    this.buildingsCompleted=false
    this.getSize();
    this.getAddons()
   
    
    if(this.selectedService.name=='Kitchen Cleaning'){
     console.log("i m coming once")
     this.otherService.type='old'
   /*   $('.more-services').html(`
      <div class="owl-carousel"  id="otherServiceCarousel" v-if="serviceChange" >
      <div class="more-service-card-active">
        <div class="text-center">Oven</div>
        <div class="text-center mt-2">
        <img src='/static/files/icons/oven.png' class="service-icon"/>
        </div>
        <div class="text-center mt-4 mb-4 p-10">
        <div class="input-group">
        <span class="input-group-btn ">
            <button type="button" class="btn btn-number cart-btn"  data-type="minus" data-field="quant[2]">
              <span class="glyphicon glyphicon-minus"></span>
            </button>
        </span>
        <input type="text" name="quant[2]" class="form-control input-number cart-input" value="10" min="1" max="100">
        <span class="input-group-btn">
            <button type="button" class="btn  btn-number cart-btn" data-type="plus" data-field="quant[2]">
                <span class="glyphicon glyphicon-plus"></span>
            </button>
        </span>
    </div>
        </div>
      </div>


      <div class="more-service-card">
        <div class="text-center">Oven</div>
        <div class="text-center mt-2">
        <img src='/static/files/icons/oven.png' class="service-icon"/>
        </div>
        <div class="text-center mt-2 mb-2">
        <v-btn class="mt-2 mb-2" color="primary" type="primary">
          Add
        </v-btn>
        </div>
      </div>
      

      <div class="more-service-card">
        <div class="text-center">Oven</div>
        <div class="text-center mt-2">
        <img src='/static/files/icons/oven.png' class="service-icon"/>
        </div>
        <div class="text-center mt-2 mb-2">
        <v-btn class="mt-2 mb-2" color="primary" type="primary">
          Add
        </v-btn>
        </div>
      </div>

     </div>
      `)*/
    /*  $('.more-services').html(`
      <div class="owl-carousel"  id="otherServiceCarousel" v-if="serviceChange" >
      <div class="more-service-card" v-for="(addon,index) in addons_parsed" v-bind:key="index">
      <div class="text-center"><% addon.details.name %></div>
      <div class="text-center mt-2">
      <img src='/static/files/icons/oven.png' class="service-icon"/>
      </div>
      <div class="text-center mt-2 mb-2">
      <v-btn class="mt-2 mb-2" color="primary" type="primary">
        Add
      </v-btn>
      </div>
    </div>
      </div>
      `)
      console.log("i ran once")
      $('#otherServiceCarousel').owlCarousel({
        loop:false,
          
          responsiveClass:true,
          responsive:{
              0:{
                  items:1,
                  nav:false
              },
              600:{
                  items:1,
                  nav:false
              },
              1000:{
                  items:6,
                  nav:false,
                  loop:false
              }
          }
      });
      this.otherService.type="old"*/
      
    }
   
     this.serviceChange=true 
   
   
  
    
   
  },
  getHourly(){
    if(this.multiServicesBill.length==0)
    {
    return(
   ` <div class="sr-service-card m-2 p-2 "   onclick="selectService('Hourly Cleaning',this)">
  <i class="far fa-circle inactive-icon"></i>
  <img src="/static/files/icons/hourly_cleaning.png" class="service-icon"> 
  <div class="text-center pt-2 service-title">
 Hourly Cleaning
</div></div>`)
    }
    else{
      return ''
    }
  },
  selectCategory(item){
    var carousel = $("#service-carousel");
    carousel.owlCarousel('destroy'); 

    this.ser_counter++
    this.refresh++
    this.currentServices=[]
this.detailedCleaningServices=[]
this.specialCareServices=[]
this.kitchenCleaningServices=[]
this.infectionControlServices=[]
    this.selectedCategory=item
    /*<div class="sr-service-card m-2 p-2"  onclick="selectService('Facade Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/FacadeCleaning.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Facade Cleaning
  </div></div>*/
    if(item=='Detailed Cleaning'){
      $('#service-carousel').html(`
      <div class="sr-service-card m-2 p-2 service-one"  onclick="selectService('General Cleaning',this)">
      <i class="far fa-circle inactive-icon"></i>
      <img src="/static/files/icons/booking/icons/detailed_cleaning.png" class="service-icon"> 
      <div class="text-center pt-2 service-title">
      General Cleaning
    </div></div>
    <div class="sr-service-card m-2 p-2 "  onclick="selectService('Deep Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/deepcleaning.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Deep Cleaning
  </div>
  </div>
  
   
  
    
 
    <div class="sr-service-card m-2 p-2"  onclick="selectService('Storage Area',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/StorageArea.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Storage Area
  </div></div>
 
    <div class="sr-service-card m-2 p-2"  onclick="selectService('Car Parking Umbrella',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/car.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Car Parking Umbrella
  </div></div>
  
    <div class="sr-service-card m-2 p-2"  onclick="selectService('Window Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/WindowCleaning.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Window Cleaning
  </div></div>
 
    <div class="sr-service-card m-2 p-2"  onclick="selectService('Outdoor Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/outdoorCleaning.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Outdoor Cleaning
  </div></div>
  
  ` +this.getHourly()
    )
    selectServiceOnly('General Cleaning')
   
    }
    else{
       if(item=='Special Care'){
      /* for(var i=0;i<this.services.length;i++){
         if(this.services[i].name=='Upholstery Cleaning'||this.services[i].name=='Carpet Cleaning'||this.services[i].name=='Mattress Cleaning'){
             this.specialCareServices.push(this.services[i])
              this.currentServices.push(this.services[i])
               this.selectedService={name:'Upholstery Cleaning'}
                this.serviceType='Upholstery Cleaning'
         }
    
    }*/
    $('#service-carousel').html(`
   
    <div class="sr-service-card m-2 p-2 service-one"  onclick="selectService('Upholstery Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/UpholsteryCleaning.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Upholstery Cleaning
  </div></div>
  
    <div class="sr-service-card m-2 p-2"  onclick="selectService('Mattress Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/bed.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Mattress Cleaning
  </div></div>
  
    <div class="sr-service-card m-2 p-2"  onclick="selectService('Carpet Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/carpet.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Carpet Cleaning
  </div></div>
    `)
    selectServiceOnly('Upholstery Cleaning')
    }
     else{
        if(item=='Kitchen Cleaning'){
     /* for(var i=0;i<this.services.length;i++){
         if(this.services[i].name=='Kitchen Cleaning'){
             this.kitchenCleaningServices.push(this.services[i])
              this.currentServices.push(this.services[i])
               this.selectedService={name:'Kitchen Cleaning'}
                this.serviceType='Kitchen Cleaning'
         }
    
    }*/
    $('#service-carousel').html(`
   
    <div class="sr-service-card m-2 p-2 service-one"   onclick="selectService('Kitchen Cleaning',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/kitchen.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Kitchen Cleaning
  </div></div>

  <div class="sr-service-card m-2 p-2 "   onclick="selectService('Kitchen Appliances',this)">
  <i class="far fa-circle inactive-icon"></i>
  <img src="/static/files/icons/appliances.png" class="service-icon"> 
  <div class="text-center pt-2 service-title">
  Kitchen Appliances
</div></div>
  
   
    `)
    selectServiceOnly('Kitchen Cleaning')
    
        }
        else{
           if(item=='Infection Control'){
          /*     for(var i=0;i<this.services.length;i++){
         if(this.services[i].name=='Sterilization'){
             this.infectionControlServices.push(this.services[i])
              this.currentServices.push(this.services[i])
               this.selectedService={name:'Sterilization'}
                this.serviceType='Sterilization'
         }
    
    }*/
    $('#service-carousel').html(`
   
    <div class="sr-service-card m-2 p-2 service-one"  onclick="selectService('Sterilization',this)">
    <i class="far fa-circle inactive-icon"></i>
    <img src="/static/files/icons/booking/icons/sanitisation.png" class="service-icon"> 
    <div class="text-center pt-2 service-title">
    Sterilization
  </div></div>
  
   
    `)
    selectServiceOnly('Sterilization')
           }
        }
        
    }
   
     
    
    
    }
    $('.owl-item:empty').remove()
 this.getSize();
 carousel.owlCarousel(
  {
    loop:false,
    navText:["<i class='fa fa-chevron-left service-control' @click='prevService()'></i>",
    "<i class='fa fa-chevron-right service-control'></i>"],
responsiveClass:true,
responsive:{
    0:{
        items:1,
        nav:false,
        loop:true
    },
    600:{
        items:4,
        nav:false
    },
    1000:{
        items:5,
        nav:true,
        loop:false
    }
}
}).trigger('refresh.owl.carousel');

   
  },
  bookMultipleService(){
    this.submit_loader=true
    const urlSearchParams = new URLSearchParams(window.location.search);
    const params = Object.fromEntries(urlSearchParams.entries());
   this.userid=window.location.href.split('/')[5]
   var posturl=''
   if(this.scheduleStatus){
     posturl='/customer/evaluatorbookingmultiplephase2/together/'
   
    axios
      .post(
         this.url+posturl+this.userid+'/',this.serviceDetails
       
      )
      .then((response) => {
        this.submit_loader=false
        console.log("booking details is "+response)
        this.phase2Result=response.data
        if(response.data.success)
        {
        this.responseText='Booking Successful'
        this.snackbar=true
       // this.getBookingDetails(response.data.booking_id)
     this.last_image_stat=true
    this.uploadImages()
    //window.location.href='/common/makequatation/phase1/'+params.enquiry_id+'/'+params.evaluation_id

        }
        else{
          this.responseText=response.data.Error
          this.snackbar=true
        }
      })
       .catch((error) => {
        this.responseText=error
        console.log(error);
      });
    }
    else{
     this.seperateMultiBook()
    }
  },
  async seperateMultiBook(){
    const urlSearchParams = new URLSearchParams(window.location.search);
    const params = Object.fromEntries(urlSearchParams.entries());
   this.userid=window.location.href.split('/')[5]
    var  posturl='/customer/evaluatorbookingmultiplephase2/together/'
    
    for(var sch in this.scheduleGroup)
    {
      this.submit_loader=true
      var totalCost=0
    var estimatedCost=0
      var groupData={}
    for(var i=0;i<this.scheduleGroup[sch].length;i++){
      var data=this.scheduleGroup[sch]
      console.log("service details is"+JSON.stringify(this.serviceDetails))
      groupData[i]={...this.serviceDetails.service_details[data[i]]}
      totalCost=totalCost+this.serviceDetails.service_details[data[i]].total_cost
    }
   // var res=await this.seperateBookRequest(posturl,totalCost,groupData)
   var res=await axios
   .post(
      this.url+posturl+this.userid+'/',
      {
        estimated_cost:totalCost,
        total_cost:totalCost,
        service_details:groupData
      }
    
   )
   .then((response) => {
     this.submit_loader=false
     console.log("booking details is "+response)
     this.phase2Result=response.data
     groupData={}
     if(response.data.success)
     {
     this.responseText='Booking Successful'
     this.snackbar=true
  
   console.log("got response")
      var schedule_keys=Object.keys(this.scheduleGroup)
      if(sch==this.scheduleGroup[schedule_keys[schedule_keys.length-1]])
      {
        this.last_image_stat=true
      }
      else{
        this.last_image_stat=false
      }
      this.uploadImages()
     return response
 
     }
     else{
       this.responseText=response.data.Error
       this.snackbar=true
     }
     
     
   })
    .catch((error) => {
     this.responseText=error
     console.log(error);
     return error
   });
    console.log("firing next ")


  }
  },

  /* This function is deprecated -> keeping it for future purpose*/
  async seperateBookRequest(posturl,totalCost,groupData){
    axios
    .post(
       this.url+posturl+this.userid+'/',
       {
         estimated_cost:totalCost,
         total_cost:totalCost,
         service_details:groupData
       }
     
    )
    .then((response) => {
      this.submit_loader=false
      console.log("booking details is "+response)
      this.phase2Result=response.data
      groupData={}
      if(response.data.success)
      {
      this.responseText='Booking Successful'
      this.snackbar=true
    
    console.log("got response")
   
       this.uploadImages()
       return response
  
      }
      else{
        this.responseText=response.data.Error
        this.snackbar=true
      }
      
      
    })
     .catch((error) => {
      this.responseText=error
      console.log(error);
      return error
    });
  },
   /* Deprecated function ends here */

  bookCustService(){
    this.userid=window.location.href.split('/')[5]
    const urlSearchParams = new URLSearchParams(window.location.search);
    const params = Object.fromEntries(urlSearchParams.entries());
   
   
     axios
       .post(
        this.url+'/customer/evaluatorbookingmultiplephase2/customer/'+this.userid+'/',this.serviceDetails
        
       )
       .then((response) => {
         
         console.log("booking details is "+response)
         this.phase2Result=response.data
         if(response.data.success)
         {
         this.responseText='Booking Successful'
         this.snackbar=true
        // this.getBookingDetails(response.data.booking_id)
        this.last_image_stat=true
      
     this.uploadImages()
    // window.location.href='/common/makequatation/phase1/'+params.enquiry_id+'/'+params.evaluation_id
         }
       })
        .catch((error) => {
         this.responseText=error
         console.log(error);
       });
  },
  uploadImages(){
    const urlSearchParams = new URLSearchParams(window.location.search);
    const params = Object.fromEntries(urlSearchParams.entries());
   for(var i=0;i<this.multiServiceImages.length;i++){
    this.submit_loader=true
     var image=new FormData()
      image.append('evaluation_book_id',Object.keys(this.phase2Result.evaluation_book_ids)[i])
      for(var j=0;j<this.multiServiceImages[i].images.length;j++){
        image.append('media',this.multiServiceImages[i].images[j].file)
      }
       axios
      .post(
         this.url+"/customer/bookingmediasave",image
       
      )
      .then((response) => {
        this.submit_loader=false
        
       if(this.last_image_stat){
        window.location.href='/common/makequatation/phase1/'+params.enquiry_id+'/'+params.evaluation_id
       }
     
       
      })
       .catch((error) => {
        console.log(error);
        if(this.last_image_stat){
          window.location.href='/common/makequatation/phase1/'+params.enquiry_id+'/'+params.evaluation_id
         }
      });

   }
    
  },
  getBookingDetails(bkid){
    axios
      .get(
         this.url+"/customer/bookingphase3?booking_id="+bkid
       
      )
      .then((response) => {
        this.bookingMultiData=response.data
        this.udf3=response.data.order_details.order_status
        var order_no=response.data.order_details.order_no
       this.gateway_eval=order_no.substring(3,order_no.length)+response.data.encryption_key
       this.gateway_price=response.data.order_details.total_amount

        
      })
       .catch((error) => {
        console.log(error);
      });
  },
  async getAddons(){
    this.addons=[]
    var ser = 'Kitchen Cleaning'
    axios.get(this.url+'/customer/ajax/getserviceaddons?service_type='+ser).then(response=>{
      this.addons=response.data.service_addons
     this.parseAddons()
     
    }).catch((error)=>{
      console.log(error)
    })
  },
  findAddons(addon){
  
    for(var i=0;i<this.addons_parsed.length;i++){
      if(this.addons_parsed[i].details.name==addon){
        return i
      }
    }
    return 'not found'
  },
  async parseAddons(){
    this.addons_parsed=[]
    for(var i=0;i<this.addons.length;i++){
      if(this.addons[i].category){
        // if(this.addons[i].name=='New Cabinet'||this.addons[i].name=='Used Cabinet'){
        //   if(this.otherService.type=='old' && this.addons[i].name=='Used Cabinet'){
        //   var add_on_stat=this.findAddons('Cabinet')
        //   }
        //   else if(this.otherService.type=='new' && this.addons[i].name=='New Cabinet'){
        //     var add_on_stat=this.findAddons('Cabinet')
        //   }
        //   else{
        //     add_on_stat='not found'
        //   }
        // }
        // else{
        var add_on_stat=this.findAddons(this.addons[i].name)
        
        if(add_on_stat!='not found'){
          this.addons_parsed[add_on_stat].size.push({
            size:this.addons[i].category,
            max_size:this.addons[i].size,
            price:this.addons[i].price
          })
        }
        else{
       
          
        this.addons_parsed.push({
          details:this.addons[i],
          selected:false,
          quantity:0,  
          size:[{
            size:this.addons[i].category,
            max_size:this.addons[i].size,
            price:this.addons[i].price
          }],
          selected_size:{}
        })
      
      }
      }
      else{
      this.addons_parsed.push({
        details:this.addons[i],
        selected:false,
        quantity:0,
        
        size:[],
        selected_size:{}
      })
    }
     

    }
    var delayInMilliseconds = 1000; //1 second

setTimeout(function() {
  $('#otherServiceCarousel').owlCarousel({
    loop:false,
   
      responsiveClass:true,
     
      navText:["<i class='fa fa-chevron-left service-control' @click='prevService()'></i>",
      "<i class='fa fa-chevron-right service-control'></i>"],
      responsive:{
          0:{
              items:1,
              nav:true
          },
          600:{
              items:1,
              nav:true
          },
          1000:{
              items:5,
              nav:true,
              loop:false
          }
      }
  });
}, delayInMilliseconds);
 
    
    
  },
  selectAddons(index){
    this.addons_parsed[index].selected=true
    this.addons_parsed[index].quantity=1
  },
 increaseQty(index){
  this.addons_parsed[index].quantity++
 },
 reduceQty(index){
  this.addons_parsed[index].quantity--
  if( this.addons_parsed[index].quantity==0){
    this.addons_parsed[index].selected=false
  }
 },
  getMultipleSlots(){
    this.slot_loader=true
    var schedule_services=this.schedule_serviceTypes
    if(this.checkKitchen()){
      schedule_services.push('Kitchen Cleaning')
    }
    
    axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:schedule_services,cleaning_date:this.slotDate,number_of_cleaners:this.selectedDuration.cleaners}
       
      )
      .then((response) => {
        this.slot_loader=false
         this.timeSlots = response.data.slotes;
         this.parseOneTimeSlots()
         if(response.data.Error){
           this.errMsg=response.data['Error']
         }
         else{
           this.errMsg=''
         }
        if (!this.time_slot.hasOwnProperty(this.slotDate)) {
          this.time_slot[this.slotDate] = {
            selectedSlot: [],
          };
        }

        this.parseSize();
      })
       .catch((error) => {
        console.log(error);
      });
  },
  parseOneTimeSlots(){
    this.parsedTimeSlots=[]
    this.available_slotes=[]
    for(var i in this.timeSlots){
      if(this.timeSlots[i].includes(2)){
        var slotNo=(parseInt(i)+2)/2
        this.available_slotes.push(slotNo)
        this.parsedTimeSlots.push(this.slotFormat[String(slotNo)])
        
        
      }
    }
  },
  getTimeSlots() {
    this.timeSlots = {};
    axios
      .get(
         this.url+"/customer/ajax/getcleaningslotes?service_type=" +
          this.serviceType +
          "&number_of_cleaners=" +
          this.selectedDuration.cleaners +
          "&cleaning_date=" +
          this.slotDate
        
      )
      .then((response) => {
        this.timeSlots = response.data.slotes;
        if (!this.time_slot.hasOwnProperty(this.slotDate)) {
          this.time_slot[this.slotDate] = {
            selectedSlot: [],
          };
        }

        this.parseSize();
      })
      .catch((error) => {
        console.log(error);
      });
  },
  parseTimeSlots() {
    /*
          3:Array[4]
          0:3
          1:6
          2:9
          3:12


*/
  },
getAreaTypes() {
    axios
      .get(
       this.url+"/customer/ajax/getareatypes"
      )
      .then((response) => {
        this.area_types = response.data['area_types'];
       
      })
      .catch((error) => {
        console.log(error);
      });
  },
  getSize() {
    var service=this.serviceType
    if(service=='Hourly Cleaning'){
      service='General Cleaning'
    }
    axios
      .get(
       this.url+"/customer/ajax/getservicesizeprice?service_type=" + service
      )
      .then((response) => {
        this.serviceSize = response.data;
        this.parseSize();
         this.facadeFilter();
         this.windowFilter();
      })
      .catch((error) => {
        console.log(error);
      });
  },
  setDuration(hours, cleaners) {
      
    this.duration.push({
      hours: hours,
      cleaners: cleaners,
    });
  },
  sortDuration(){
    if(this.duration[0].hours<this.duration[1].hours){
     this.selectDuration(this.duration[0])
    }
    else{
      var temp=this.duration[0]
      this.duration[0]=this.duration[1]
      this.duration[1]=temp
      this.selectDuration(this.duration[0])
    }
  },
  parseSize() {
    this.sizeData = [];
    console.log("servuc size is " + this.serviceSize);
    for (var i in this.serviceSize) {
      this.serviceSize[i]["combinedSize"] =
        this.serviceSize[i].name +
        " ( " +
        this.serviceSize[i].min_size +
        " sq. m - " +
        this.serviceSize[i].max_size +
        " sq. m )";
      this.sizeData.push(this.serviceSize[i]);
    }
    this.serviceSize = {};
  },
  save(date) {
    this.$refs.menu.save(date);
  },
  async onImageFileChanged(event) {
    
    this.ImageDetails.service=this.selectedService.name;
    console.log("orginal file size is"+event.target.files[0].size)
    var file=event.target.files[0]
 
  const options = {
  maxSizeMB: 1,
  maxWidthOrHeight: 1920,
  useWebWorker: true,
  onProgress:Function(2)
}
try {
  const compressedFile = await imageCompression(event.target.files[0], options);
  console.log('compressedFile instanceof Blob', compressedFile instanceof Blob); // true
  console.log(`compressedFile size ${compressedFile.size / 1024 / 1024} MB`); // smaller than maxSizeMB

  await this.uploadImgToArray(compressedFile,event.target.files[0].name); // write your own logic
} catch (error) {
  console.log(error);
}
  
  
  },
  uploadImgToArray(file,fileName){
    file.lastModifiedDate = Date.now();
  
  var converted_file = new File([file],  fileName,{lastModified: Date.now()});
    console.log("file size is "+converted_file.size)
    this.ImageDetails.url = URL.createObjectURL(converted_file);
    this.ImageDetails.file = converted_file;
    this.imageData.push(this.ImageDetails);
    this.ImageDetails = {
      file: "",
      url: "",
      service:""
      
    };
  },
  deleteImage(imageindex) {
    this.imageData.splice(imageindex, 1);
  },

  addNew() {
    this.otherService = {
      material: "",
      color: "",
      size: "",
      type: "",
      age: "",
      stain: false,
      is_cabinet:false,
      stain_reason: "",
      wall_type: "",
      floor_type: "",
      ceiling_type: "",
      residue: false,
      hallway_size: "",
      sides: "",
      stain_age: "",
      height:"",
      keynote_data:[],
      addons:[]
    };
    this.parseAddons()
    if(this.selectedService.name=='Kitchen Cleaning'){
      this.otherService.type="old"
      this.changeKitchen()
    }
  
    this.dialog = true;
    this.dialogmsg = "Add New";
    this.dialogStat = true;
    this.building = [];
    var delayInMilliseconds=1000
    var carousel = $("#otherServiceDialogCarousel");
    carousel.owlCarousel('destroy'); 
    $('.owl-item:empty').remove()
    setTimeout(function() {
      $('#otherServiceDialogCarousel').owlCarousel({
        loop:false,
       
          responsiveClass:true,
          navText:["<i class='fa fa-chevron-left service-control' @click='prevService()'></i>",
          "<i class='fa fa-chevron-right service-control'></i>"],
          responsive:{
              0:{
                  items:1,
                  nav:true
              },
              600:{
                  items:1,
                  nav:true
              },
              1000:{
                  items:3,
                  nav:true,
                  loop:false
              }
          }
      });
    }, delayInMilliseconds);
    $('#otherServiceDialogCarousel').removeClass('owl-hidden')
  },
  facadeFilter(){
      this.facadeSize=[]
      if(this.hallway_check){
          for(var i=0;i<this.sizeData.length;i++){
              if(this.sizeData[i].is_highprice_facade){
                  this.facadeSize.push(this.sizeData[i])
              }
          }
      }
      else{
         
          for(var i=0;i<this.sizeData.length;i++){
              if(!this.sizeData[i].is_highprice_facade){
                  this.facadeSize.push(this.sizeData[i])
              }
          }
      
      }
  },
  windowFilter(){
    this.windowSize=[]
    this.otherService.size={}
    if(this.window_check){
        for(var i=0;i<this.sizeData.length;i++){
            if(this.sizeData[i].is_highprice_window){
                this.windowSize.push(this.sizeData[i])
            }
        }
    }
    else{
       
        for(var i=0;i<this.sizeData.length;i++){
            if(!this.sizeData[i].is_highprice_window){
                this.windowSize.push(this.sizeData[i])
            }
        }
    
    }
},
  editItem(a, b) {
    this.edit_item=true
    this.add_new_kitchen=false
    this.addons_parsed=[...a.addons]
  
      this.dialog = true;
      this.dialogmsg = "Edit";
      this.dialogStat = false;
    
  
    (this.otherService = {
      material: a.material,
      keynote_data:a.keynote_data,
      color: a.color,
      size: a.size,
      type: a.type,
      age: a.age,
      stain: a.stain,
      stain_reason: a.stain_reason.split(','),
      wall_type: a.wall_type,
      floor_type: a.floor_type,
      ceiling_type: a.ceiling_type,
      residue: a.residue,
      hallway_size: a.hallway_size,
      sides: a.sides,
      stain_age: a.stain_age,
      section_cost:a.section_cost,
      height:a.height,
      addons:a.addons,
      is_cabinet:a.is_cabinet

    }),
   
      this.currentItem = b;
      var delayInMilliseconds=1000
    var carousel = $("#otherServiceDialogCarousel");
    carousel.owlCarousel('destroy'); 
    $('.owl-item:empty').remove()
    setTimeout(function() {
      $('#otherServiceDialogCarousel').owlCarousel({
        loop:false,
        navText:["<i class='fa fa-chevron-left service-control' @click='prevService()'></i>",
      "<i class='fa fa-chevron-right service-control'></i>"],
          responsiveClass:true,
          responsive:{
              0:{
                  items:1,
                  nav:true
              },
              600:{
                  items:1,
                  nav:true
              },
              1000:{
                  items:3,
                  nav:true,
                  loop:false
              }
          }
      });
    }, delayInMilliseconds);
    $('#otherServiceDialogCarousel').removeClass('owl-hidden')
  },
  async saveChanges() {
    this.edit_item=false
      await this.calcSize()
      
       if(this.otherService.stain_reason.length>0){
         this.otherService.stain_reason=this.otherService.stain_reason.join()
       }
       this.otherService.sectiononly_cost=this.otherService.size.cost
       this.otherService.section_cost=this.otherService.size.cost+this.findAddonCost()
    this.otherServices[this.currentItem] = { ...this.otherService };
    this.billingData[this.currentItem].section_cost=this.otherService.section_cost
    this.billingData[this.currentItem].section_net_cost=this.otherService.section_cost
    this.billingData[this.currentItem].sectiononly_cost=this.otherService.sectiononly_cost
    this.billingData[this.currentItem].sectiononly_net_cost=this.otherService.sectiononly_cost
    this.billingData[this.currentItem].section={ ...this.otherService }
    this.dialog = false;
    this.otherService={
      material: "",
      addons:[],
      color: "",
      size: {},
      type: "",
      age: "",
      stain: false,
      stain_reason: "",
      wall_type: "",
      floor_type: "",
      ceiling_type: "",
      residue: false,
      is_cabinet:false,
      hallway_size: "",
      sides: "",
      stain_age: "",
      height:"",
      keynote_data:[],
      section_cost:0,
      sectiononly_cost:0
    },
   this.recalcCost();
  },
  calcSize() {
    var sizeFound=false
    var max_size_data=[]
    var max_size_val=[]
    if (this.serviceType == "Upholstery Cleaning") {
      console.log("service test passed");
     /* if (this.otherService.type == "CHAIR") {
        for (var item = 0; item < this.sizeData.length; item++) {
          console.log("type test passed");
         
          if (this.sizeData[item].upholstery_type == "CHAIR") {
             max_size_data.push(this.sizeData[item].max_size)
             max_size_val.push(this.sizeData[item])
            if (
              this.otherService.size >= this.sizeData[item].min_size &&
              this.otherService.size <= this.sizeData[item].max_size
            ) {
              this.otherService.size = this.sizeData[item];
              sizeFound=true
              console.log("size test passed");
            }
          }
        }
        var max_val=Math.max(...max_size_data)
        var left_size=0
        console.log('max val is '+max_val)
        if(!sizeFound && this.otherService.size>0){
          left_size=this.otherService.size-max_val
          
          for(var j=0;j<max_size_val.length;j++){
            if(max_size_val[j].max_size==max_val){
              var new_cost=left_size*max_size_val[j].unit_price
              var current_cost=max_size_val[j].cost+new_cost
              var size=this.otherService.size
              this.otherService.size={
                name: "Custom size",
                cost: current_cost,
                max_size:size,
                min_size:size,
                upholstery_type: "CHAIR",
                combinedSize:size+' Seater'

              }
            }
          }
      }
      }*/
      if (this.otherService.type == "SOFA") {
        for (var item = 0; item < this.sizeData.length; item++) {
          console.log("type test passed");
          if (this.sizeData[item].upholstery_type == "SOFA") {
            for (var item = 0; item < this.sizeData.length; item++) {
          console.log("type test passed");
         
          if (this.sizeData[item].upholstery_type == "SOFA") {
             max_size_data.push(this.sizeData[item].max_size)
             max_size_val.push(this.sizeData[item])
            if (
              this.otherService.size >= this.sizeData[item].min_size &&
              this.otherService.size <= this.sizeData[item].max_size
            ) {
              this.otherService.size = this.sizeData[item];
              sizeFound=true
              console.log("size test passed");
            }
          }
        }
        var max_val=Math.max(...max_size_data)
        var left_size=0
        console.log('max val is '+max_val)
        if(!sizeFound && this.otherService.size>0){
          left_size=this.otherService.size-max_val
          
          for(var j=0;j<max_size_val.length;j++){
            if(max_size_val[j].max_size==max_val){
              var new_cost=this.otherService.size*max_size_val[j].unit_price
              var current_cost=max_size_val[j].cost+new_cost
              var size=this.otherService.size
              this.otherService.size={
                name: size+' Seater',
                cost: new_cost,
                max_size:size,
                min_size:size,
                upholstery_type: "SOFA",
                combinedSize:size+' Seater'

              }
            }
          }
      }
          }
        }
      }
      if (this.otherService.type == "CURTAIN") {
        for (var item = 0; item < this.sizeData.length; item++) {
          console.log("type test passed");
          if (this.sizeData[item].upholstery_type == "CURTAIN") {
            if (
              this.otherService.size >= this.sizeData[item].min_size &&
              this.otherService.size <= this.sizeData[item].max_size
            ) {
              this.otherService.size = this.sizeData[item];
              console.log("size test passed");
            }
          }
        }
      }
    }
  },
  async addOtherService() {
       if(this.$refs.otherServiceForm.validate())
     { 

    await this.calcSize();
    this.otherService.section_cost=this.otherService.size.cost+this.findAddonCost()
    this.otherService.sectiononly_cost=this.otherService.size.cost
   if(this.otherService.stain_reason.length>0){
     this.otherService.stain_reason=this.otherService.stain_reason.join()
   }
   if(this.serviceType=='Kitchen Cleaning'){
     this.otherService.addons=[...this.addons_parsed]
   }
    this.otherServices.push(this.otherService);
    if(this.serviceType=='Upholstery Cleaning')
    {
    this.billingData.push({
      name: this.serviceType + " - " + this.otherService.type,
      section_name: this.serviceType + " - " + this.otherService.type,
      section: this.otherService,
      section_cost:this.otherService.section_cost,
      section_net_cost:this.otherService.section_cost,
     
      sectiononly_cost:this.otherService.sectiononly_cost,
      sectiononly_net_cost:this.otherService.sectiononly_cost
    });
    }
    else{
       this.billingData.push({
      name: this.serviceType ,
      section_name: this.serviceType,
      section: this.otherService,
      section_cost:this.otherService.section_cost,
      section_net_cost:this.otherService.section_cost,
      sectiononly_cost:this.otherService.sectiononly_cost,
      sectiononly_net_cost:this.otherService.sectiononly_cost
    });
    }
   
    this.otherService = {
      material: "",
      color: "",
      size: "",
      type: "old",
      is_cabinet:false,
      age: "",
      stain: false,
      stain_reason: "",
      keynote_data:[],
      wall_type: "",
      floor_type: "",
      ceiling_type: "",
      residue: false,
      hallway_size: "",
      sides: "",
      stain_age: "",
      section_cost:null,
      sectiononly_cost:null,

    
      addons:[]
    };
    this.parseAddons()
    this.dialog = false;
     }
      this.findTempcost()
  },
    async addOtherServiceDialog() {
       if(this.$refs.otherServiceDialogForm.validate())
     { 

    await this.calcSize();
    this.otherService.section_cost=this.otherService.size.cost+this.findAddonCost()
    this.otherService.sectiononly_cost=this.otherService.size.cost
    if(this.otherService.stain_reason.length>0){
      this.otherService.stain_reason=this.otherService.stain_reason.join()
    }
    if(this.serviceType=='Kitchen Cleaning'){
      this.otherService.addons=[...this.addons_parsed]
    }
    this.otherServices.push(this.otherService);
    if(this.serviceType=='Upholstery Cleaning')
    {
       this.billingData.push({
      name: this.serviceType + " - " + this.otherService.type,
      section_name: this.serviceType + " - " + this.otherService.type,
      section: this.otherService,
      sectiononly_cost:this.otherService.sectiononly_cost,
      sectiononly_net_cost:this.otherService.sectiononly_cost,
      section_cost:this.otherService.section_cost,
      section_net_cost:this.otherService.section_cost
    });
    }
    else{
        this.billingData.push({
      name: this.serviceType,
      section_name: this.serviceType,
      section: this.otherService,
      sectiononly_cost:this.otherService.sectiononly_cost,
      section_cost:this.otherService.section_cost,
      section_net_cost:this.otherService.section_cost
    });
    }
   
    
    this.otherService = {
      material: "",
      color: "",
      size: "",
      type: "",
      age: "",
      stain: false,
      stain_reason: "",
      wall_type: "",
      floor_type: "",
      ceiling_type: "",
      is_cabinet:false,
      residue: false,
      hallway_size: "",
      sides: "",
      stain_age: "",
      section_cost:null,
      section_net_cost:null,
      sectiononly_cost:null,
      sectiononly_net_cost:null,
      keynote_data:[]
    };
    this.dialog = false;
     }
      this.findTempcost()
  },
  recalcCost(){
      this.totalCost=0;
      for(var i=0;i<this.billingData.length;i++){
          this.totalCost=this.totalCost+this.billingData[i].section.section_cost
      }
  },
  findServiceCost(){
  
     for(var i=0;i<this.multiServicesBill.length;i++){
         var servcost=0;
          for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
            servcost = servcost + this.multiServicesBill[i].bill[j].section_cost
          }
          console.log("serv cost is "+servcost)
          this.multiServicesBill[i]['total_cost']=servcost
     }

  },
  
  deleteItem(a) {
    this.otherServices.splice(a, 1);
    this.billingData.splice(a,1)
    this.recalcCost()
  },
  goToServices(){
    
    console.log('i m here')
    
  this.activeTab='Services'
  setTimeout(function (){

    app.reinitCat()
    app.selectCategory('Detailed Cleaning')
  }, 500);
  
 
  $('#tab-1').click()
  
  },
  reinitCat(){
    $('#category-carousel').owlCarousel('destroy'); 
    $('#category-carousel').owlCarousel({
      loop:false,
      
      responsiveClass:true,
      responsive:{
          0:{
              items:1,
              nav:false
          },
          600:{
              items:4,
              nav:false
          },
          1000:{
              items:5,
              nav:false,
              loop:false
          }
      }
  }).trigger('refresh.owl.carousel');
  },
  goToSchedule(){
    
    if(!this.editScheduleStat){
      this.resetScheduler()
    }
    
      this.activeTab='Schedule'
      this.currentPageTitle='Schedule'
      if(this.scheduleStat && !this.editScheduleStat){
        this.addAllServiceTypes()
      }
      this.findSelectedTotalSize()
      this.calcSelectedServices()
      this.newdurationcalculation();
      if(this.serviceType=='Hourly Cleaning'){
        this.cleaningPolicy='Subscription'
      }

  },
  
  checkEditSchedule(){
    if(Object.keys(this.editScheduleData).length>0){
      if(Object.keys(this.editScheduleData.schedule_details).length>0){
        return false
      }
      else{
        return true
      }
    }
    else {
      return true
    }
    
  },
  goToBilling(){
      this.activeTab='Payment Method'
      this.arrangeData();
  },
  addMoreService(){
    reinit()
    this.serviceCount++
    this.activeTab='Services'
   
  },
   goToCart(){
    if(this.serviceType=='Kitchen Appliances'){
      var otherService={
        material: "",
        addons:[],
        color: "",
        size: {},
        section_cost:this.findAddonCost(),
        sectiononly_cost:0,
        type: "",
        age: "",
        stain: false,
        stain_reason: "",
        wall_type: "",
        floor_type: "",
        ceiling_type: "",
        residue: false,
        is_cabinet:false,
        hallway_size: "",
        sides: "",
        stain_age: "",
        height:"",
        keynote_data:[]
      }
      otherService.addons=[...this.addons_parsed]
      var serviceData={
        name:'',
        section_cost:'',
        section_net_cost:'',
        sectiononly_cost:'',
        sectiononly_net_cost:'',
        section:otherService
      }
      serviceData.name='Kitchen Appliances'
      serviceData.section_name='Kitchen Appliances'
      serviceData.section_cost=this.findAddonCost()
      serviceData.section_net_cost=this.findAddonCost()
      serviceData.sectiononly_cost=0
      serviceData.sectiononly_net_cost=0
      this.billingData.push(serviceData)
      this.parseAddons()
    }
    if(this.serviceType=='Hourly Cleaning'){
      this.billingData[0].section_net_cost=0
      this.billingData[0].section_cost=0
      this.billingData[0].sectiononly_net_cost=0
      this.billingData[0].sectiononly_cost=0
    }
     var sampleServicesBill={
       service:'',
       bill:[],
       serviceNo:this.serviceCount,
       area_type:this.area_type,
       location_type:this.location_type,
       evaluator_note:this.evaluator_note,
       schedule_details:{},
       cleaners:null
     }
   
       this.serviceTypes.push(this.serviceType)
     
     this.multiServiceImages.push({service:this.selectedService.name,images:this.imageData})
     this.imageData=[]
     sampleServicesBill.service=this.serviceType
     Object.assign(sampleServicesBill.bill, this.billingData);

     this.multiServicesBill.push(sampleServicesBill)
       this.activeTab='Cart'
       window.scrollTo(0,0);
   sampleServicesBill={
       service:'',
       bill:[],
       serviceNo:'',
       area_type:'',
       location_type:'',
       evaluator_note:''
     }
     this.area_type=''
     this.location_type=''
     this.evaluator_note=''
     this.billingData=[]
     this.otherServices=[]
     this.otherService={
    material: "",
    addons:[],
    color: "",
    size: {},
    section_cost:0,
    sectiononly_cost:0,
    type: "",
    age: "",
    stain: false,
    stain_reason: "",
    wall_type: "",
    floor_type: "",
    ceiling_type: "",
    residue: false,
    is_cabinet:false,
    hallway_size: "",
    sides: "",
    stain_age: "",
    height:"",
    keynote_data:[]
  },
      this.building=[]
      this.no_of_apartments = [];
     
      this.buildingsCompleted=false
      this.serviceData.service_details.location_type=''
       this.serviceData.service_details.area_type=''
       this.e={building:[]}
      this.no_of_building=0
      this.temp_no_of_building=0
      this.no_of_floors=[]
      this.calcTotal()
       //this.findTotalSize()
       this.findSelectedTotalSize()
       this.findServiceCost()
    this.tempCost=0
      this.schedule_serviceTypes_selected=[]
      this.schedule_serviceTypes=[]
    //  this.durationcalculation();
     
      
  },
  selectServ(elem) {
    this.billingData = [];
    this.tempCost=0
    this.serviceType = elem;
    this.serviceSection.service_type = this.serviceType;
    this.otherServices = [];
    this.no_of_apartments = [];
    this.no_of_floors = [];
    this.no_of_building = 0;
      this.temp_no_of_building=0
    this.otherService = {
      material: "",
      color: "",
      size: "",
      type: "",
      age: "",
      stain: false,
      is_cabinet:false,
      addons:[],
      stain_reason: "",
      wall_type: "",
      floor_type: "",
      ceiling_type: "",
      residue: false,
      keynote_data:[],
      hallway_size: "",
      sides: "",
      
    };
    this.e = {
      building: [],
    },
      console.log("service type is" + this.serviceType);
  },
  addSectionFloor(section) {
    this.serviceSection.sections[section] = {
      size: "",
    };
  },

  setBuilding() {
    
   if(this.no_of_floors.length>0){
    
    this.building_warning=true
   }
   else{
    this.no_of_building=this.temp_no_of_building
   
    this.valid=[]
    this.building=[]
    this.e.building=[]
    this.no_of_floors=[]
    this.reset_floor=false
    this.reset_building=false
    for (var i = 0; i < this.no_of_building; i++) {
      this.building.push({
        floors: [],
        completed:false
      });
      this.e.building.push({
        floors: [],
        e: 1,
      });
      this.no_of_floors.push("")
      this.valid.push({floors:[]})
    }
   
    this.reset_floor=true
    this.reset_building=true
  }
  
  },
  setFloors(building) {
    this.building[building - 1].floors = [];
    this.valid[building-1].floors=[];
    this.e.building[building - 1].e = 1;
    for (var i = 0; i < this.no_of_floors[building - 1]; i++) {
      this.building[building - 1].floors.push({
        section_name: "",
        size: "",
      floor_type:'',
        wall_type: "",
        ceiling_type: "",
        cement_residue: false,
        section_cost: "",
        section_net_cost: "",
        keynotes: {},
        apartment: false,
        apartments: [],
        kitchen: false,
        kitchens: [],
        keynote_data:[],
        completed: false,
        paint_residue: false,
        upholsteries: ["Sofa", ""],
        
        
      });
      this.e.building[building - 1].floors.push({
        floors: [],
        e: 1,
      });
      this.valid[building-1].floors.push(false)
    }
  },
  setApartments(building, floor) {
    this.building[building - 1].floors[floor - 1].apartments = [];
    this.e.building[building - 1].floors[floor - 1].e = 1;
    for (
      var i = 0;
      i < this.building[building - 1].floors[floor - 1].no_of_apartments;
      i++
    ) {
      this.building[building - 1].floors[floor - 1].apartments.push({
        section_name: "",
        size: "",
        completed: false,
        wall_type: "",
        floor_type: "",
        ceiling_type: "",
        cement_residue: false,
        paint_residue: false,
        section_cost: "",
        section_net_cost: "",
        no_of_rooms: "",
        no_of_bathrooms: "",
        no_of_windows: "",
        keynote_data:[],
        kitchen: false,
        kitchens: [],
        keynotes: {},
      });
    }
  },
  hourlyCleaningChange(){
    this.hourly_slots=false
    this.selectedDuration.cleaners=parseInt(this.hourly_cleaning.cleaners)
    if((parseInt(this.hourly_cleaning.hourly_duration)%2) !=0 ){
      this.selectedDuration.hours=parseInt(this.hourly_cleaning.hourly_duration)+1
      this.hourly_cleaning.duration=parseInt(this.hourly_cleaning.hourly_duration)+1
    }
    else{
      this.selectedDuration.hours=parseInt(this.hourly_cleaning.hourly_duration)
      this.hourly_cleaning.duration=parseInt(this.hourly_cleaning.hourly_duration)
    }
    this.selectedDuration.slots=parseInt(this.selectedDuration.hours)/2
    
    this.hourly_slots=false
    this.calcSlots()
    this.hourly_slots=true
  },
  selectDuration(duration) {
    duration.slots = duration.hours / 2;
    this.selectedDuration = duration;
    this.resetOneTime()
    this.calcSlots()
    this.getMultipleSlots();
  },
  formatDate() {
    var slotDate = this.dateSelected;
    var slotYear = slotDate.split("-")[0];
    var slotMonth = slotDate.split("-")[1];
    var slotDay = slotDate.split("-")[2];
   /* if (slotDay[0] == 0) {
      slotDay = slotDay[1];
    }
    if (slotMonth[0] == 0) {
      slotMonth = slotMonth[1];
    }*/
    this.slotDate = slotDay + "-" + slotMonth + "-" + slotYear;
    if (this.selectedDuration.cleaners && this.serviceType && this.slotDate) {
     this.getMultipleSlots()
    }
  },
  buildingCompleteChecker(){
   
    var stat=false
    for(var i=0;i<this.building.length;i++){
      if(this.building[i].completed){
        stat=true
      }
      else{
        stat=false
        break
      }
    }
    return stat
  },
  floorCompleteChecker(building){
   
    var stat=false
    for(var i=0;i<this.building[building].floors.length;i++){
      if(this.building[building].floors[i].completed){
        stat=true
      }
      else{
        stat=false
        break
      }
    }
    return stat
  },
  apartmentCompleteChecker(building,floor){
    var stat=false
    for(var i=0;i<this.building[building].floors[floor].apartments.length;i++){
      if(this.building[building].floors[floor].apartments[i].completed){
        stat=true
      }
      else{
        stat=false
        break
      }
    }
    return stat
  },
  nextTab(build) {
    this.floor_msg=false
    this.building_msg=false
    console.log("building tab is "+build)
    console.log("building tab no is "+this.no_of_building)
    
    if(!this.floorCompleteChecker(build-1)){
      this.floor_msg=true
    }
    else{
   this.cat_counter=this.cat_counter+1
  //  if (build == this.no_of_building ) {
    if (build == this.no_of_building ) {
      if(this.buildingCompleteChecker()){
        this.buildingsCompleted = true;
      }
      else{
        this.building_msg=true
      }
     
     
    
    } else {
      console.log("id is " + build);
      document.querySelector("#tab" + (build + 1)).click();
    }
  }
  },

  changeDuration(index) {
    var currentTotal = 0;
    var balCounter = 0;
    var lastDay = 0;
    this.splitData[index].fixed = true;
    for (var i = 0; i < this.splitData.length; i++) {
      currentTotal = currentTotal + parseInt(this.splitData[i].hours);
    }

    var balance = parseInt(this.selectedDuration) - currentTotal;
    console.log("balance is " + balance);
    if (balance > 0) {
      for (var j = 0; j < this.splitData.length; j++) {
        if (!this.splitData[j].fixed) {
          for (var k = 0; k < balance; k++) {
            if (parseInt(this.splitData[j].hours) < 10) {
              this.splitData[j].hours = parseInt(this.splitData[j].hours) + 1;

              if (this.splitData[j].hours >= 10) {
                this.splitData[j].maxVal = 12;
              } else {
                this.splitData[j].maxVal = 12;
              }
              balCounter = balCounter + 1;
              break;
            }
          }
        }
      }

      var balanceamount = balance - balCounter;
      console.log("balance amount is " + balanceamount);
      if (balanceamount > 0) {
        var fullDays = 0;
        var lastDayHour = 0;
        var days = 0;
        lastDay = this.splitData.length;
        if (balanceamount > 10) {
          days = balanceamount / 10;
          fullDays = Math.floor(days);
          lastDayHour = days.toString().split(".")[1];
          for (var i = 0; i < fullDays; i++) {
            this.splitData.push({
              name: "Day " + (lastDay + 1),
              hours: "10",
              maxVal: "12",
              fixed: false,
            });
            lastDay = lastDay + 1;
          }
          if (lastDayHour > 0) {
            this.splitData.push({
              name: "Day " + lastDay,
              hours: lastDayHour,
              maxVal: "12",
              fixed: false,
            });
          }
        } else {
          this.splitData.push({
            name: "Day " + lastDay,
            hours: balanceamount,
            maxVal: "12",
            fixed: false,
          });
        }
      }
    } else {
      if (balance < 0) {
        var negBalCounter = 0;
        for (var j = 0; j < this.splitData.length; j++) {
          if (!this.splitData[j].fixed) {
            for (var k = 0; k < -1 * balance; k++) {
              if (parseInt(this.splitData[j].hours) > 0) {
                this.splitData[j].hours =
                  parseInt(this.splitData[j].hours) - 1;
                if (this.splitData[j].hours >= 10) {
                  this.splitData[j].maxVal = 12;
                } else {
                  this.splitData[j].maxVal = 12;
                }
                negBalCounter = negBalCounter + 1;
              }
            }
          }
          if (negBalCounter == -1 * balance) {
            break;
          } else {
            if (negBalCounter == 0 && -1 * balance != 0) {
              for (var m = 0; m < -1 * balance; m++) {
                if (parseInt(this.splitData[j].hours) > 0 && j != index) {
                  this.splitData[j].hours =
                    parseInt(this.splitData[j].hours) - 1;
                  if (this.splitData[j].hours >= 10) {
                    this.splitData[j].maxVal = 12;
                  } else {
                    this.splitData[j].maxVal = 12;
                  }
                  negBalCounter = negBalCounter + 1;
                }
              }
            }
          }
        }
        if (balance < 0) {
          for (var i = 0; i < this.splitData.length; i++) {
            if (parseInt(this.splitData[i].hours) == 0) {
              this.splitData.splice(i, 1);
            }
          }
        }
      }
    }
  },
  parseSize() {
    this.sizeData = [];
    for (var i in this.serviceSize) {
      this.serviceSize[i]["combinedSize"] =
        this.serviceSize[i].name +
        "( " +
        this.serviceSize[i].min_size +
        " sq. m - " +
        this.serviceSize[i].max_size +
        " sq. m )";
      this.sizeData.push(this.serviceSize[i]);
    }
  },
  checkBillingData(building,floor){
    this.billingDataIndex=null
    var itemFound = false;
    for (var i = 0; i < this.billingData.length; i++) {
      if (
        this.billingData[i].name ==
        "Building " +
          building +
          " Floor " +
          floor
      ) {
        itemFound = true;
        this.billingDataIndex=i
        break
      }
    }
    return itemFound
  },
  findBillingDataIndex(building,floor){
    this.billingDataIndex=null
    var itemFound = false;
    for (var i = 0; i < this.billingData.length; i++) {
      if (
        this.billingData[i].name ==
        "Building " +
          building +
          " Floor " +
          floor
      ) {
        itemFound = true;
       return i 
      }
    }

  },
  checkBillingApartmentData(building,floor,apartment){
    this.billingDataIndex=null
    var itemFound = false;
    for (var i = 0; i < this.billingData.length; i++) {
      if (
        this.billingData[i].name ==
        "Building " +
          building +
          " Floor " +
          floor +
          " Apartment " +
          (apartment + 1)
      ) {
        itemFound = true;
        this.billingDataIndex=i
        break
      }
    }
    return itemFound
  },
  findBillingApartmentDataIndex(building,floor,apartment){
    this.billingDataIndex=null
    var itemFound = false;
    for (var i = 0; i < this.billingData.length; i++) {
      if (
        this.billingData[i].name ==
        "Building " +
          building +
          " Floor " +
          floor +
          " Apartment " +
          (apartment + 1)
      ) {
        itemFound = true;
       return i 
      }
    }

  },
  nextApartment(building, floor, apartment) {
    //this.$refs.apartmentForm[0].validate()
      if(this.$refs['building-'+building+'floor-'+floor+'apartment-'+ apartment][0].validate()){

      
      this.building[building].floors[floor].apartments[apartment].section_cost=0
    this.e.building[building].floors[floor].e = apartment + 2;
    this.building[building].floors[floor].apartments[
      apartment
    ].completed = true;
    var itemFound = false;
    for (var i = 0; i < this.billingData.length; i++) {
      if (
        this.billingData[i].name ==
        "Building " +
          (building + 1) +
          " Floor " +
          (floor + 1) +
          " Apartment " +
          (apartment + 1)
      ) {
        itemFound = true;
        this.billingData[i].section = this.building[building].floors[
          floor
        ].apartments[apartment];
      }
    }
    if (!itemFound) {
        this.building[building].floors[floor].apartments[apartment].section_cost=this.building[building].floors[floor].apartments[apartment].size.cost
        this.building[building].floors[floor].apartments[apartment].section_net_cost= this.building[building].floors[floor].apartments[apartment].section_cost
          if(this.building[building].floors[floor].apartments[apartment].kitchen){
             
              for(var k=0;k<this.building[building].floors[floor].apartments[apartment].kitchens.length;k++){
                if(this.building[building].floors[floor].apartments[apartment].kitchens[k].type=='old'){
                  this.building[building].floors[floor].apartments[apartment].section_net_cost=this.building[building].floors[floor].apartments[apartment].section_net_cost+this.building[building].floors[floor].apartments[apartment].kitchens[k].size.cost
              }

              }
          }
       
      this.billingData.push({
        name:
          "Building " +
          (building + 1) +
          " Floor " +
          (floor + 1) +
          " Apartment " +
          (apartment + 1),
          section_name: "Building " +
          (building + 1) +
          " Floor " +
          (floor + 1) +
          " Apartment " +
          (apartment + 1),
        section: this.building[building].floors[floor].apartments[apartment],
        section_cost:this.building[building].floors[floor].apartments[apartment].section_net_cost,
           section_net_cost:this.building[building].floors[floor].apartments[apartment].section_net_cost,
           sectiononly_cost:this.building[building].floors[floor].apartments[apartment].size.cost,
           sectiononly_net_cost:this.building[building].floors[floor].apartments[apartment].size.cost,
      });
    }
  if(apartment==(parseInt(this.building[building].floors[floor].no_of_apartments)-1)){
        this.building[building].floors[floor].completed=true
  }
       

    this.recalcApartmentPrice(building,floor,apartment);
    this.findTempcost()
}
     
  },
  findTempcost(){
    this.tempCost=0
    for(var i=0;i<this.billingData.length;i++){
        this.tempCost=this.tempCost+this.billingData[i].section.section_cost
    }
  },
  checkBuildingStats(index){
    if(index>0){
    
      if(!this.floorCompleteChecker(index-1)){
        console.log("i clicked tab"+index)
        document.querySelector("#tab" + (index-1)).click();
      }
    }
  },
  nextFloor(building, floor) {
    this.apartment_stat_err=false
    this.building_msg=false
    if(this.building[building].floors[floor-1].apartment && !this.apartmentCompleteChecker(building,floor-1)){
      this.apartment_stat_err=true
    }
    else{
    this.floor_msg=false
      console.log('validate is '+this.$refs.form)
     if(this.$refs['building-'+building+'floor-'+(floor-1)][0].validate())
     { 
      console.log('validation passsed')
    this.building[building].floors[floor-1].section_cost=this.building[building].floors[floor-1].size.cost
    this.e.building[building].e = floor + 1;
    this.building[building].floors[floor - 1].completed = true;
    var floorFound = false;
   
    
       
        for (var i = 0; i < this.billingData.length; i++) {
      if (
         this.billingData[i].name ==
        "Building " + (building + 1) + " Floor " + floor
      ) {
        floorFound = true;
        this.billingData[i].section = this.building[building].floors[
          floor - 1
        ];
      }
    }
      
   
  
    if (!floorFound) {
      if (!this.building[building].floors[floor - 1].apartment) {
         this.building[building].floors[floor-1].section_cost=this.building[building].floors[floor-1].size.cost
         this.building[building].floors[floor - 1].section_net_cost=this.building[building].floors[floor-1].section_cost
          if(this.building[building].floors[floor - 1].kitchen){
             
              for(var k=0;k<this.building[building].floors[floor - 1].kitchens.length;k++){

                if(this.building[building].floors[floor - 1].kitchens[k].type=='old'){
                  this.building[building].floors[floor - 1].section_net_cost=this.building[building].floors[floor - 1].section_net_cost+this.building[building].floors[floor - 1].kitchens[k].size.cost
              }

              }
          }
         // this.building[building].floors[floor - 1].section_cost=
         this.billSample.sectiononly_cost=this.building[building].floors[floor-1].size.cost
         this.billSample.sectiononly_net_cost=this.building[building].floors[floor-1].size.cost
         this.billSample.section_cost=this.building[building].floors[floor - 1].section_net_cost
         this.billSample.section_net_cost=this.building[building].floors[floor - 1].section_net_cost
         this.billSample.name= "Building " + (building + 1) + " Floor " + floor
         this.billSample.section_name= "Building " + (building + 1) + " Floor " + floor
         this.billSample.serviceNo=this.serviceCount
         Object.assign(this.billSample.section, this.building[building].floors[floor - 1]);
        
        this.billingData.push(this.billSample);
        this.billSample={
     section_name:'',     
    name:'',
    section:{},
    section_cost:"",
    section_net_cost:"",
    sectiononly_cost:"",
    sectiononly_net_cost:"",
    serviceNo:this.serviceCount,
  }
       
      }
     
      
    }
      if (floor == this.building[building].floors.length) {
          this.building[building].completed = true;
          console.log("floor is " + floor);
          this.floorCompleted=true;
        }
        else{
          this.building[building].completed = false;
         
        }
    this.recalcPrice(building,floor-1);
     }
      this.findTempcost()
    }
  },
  recalcPrice(building,floor) {
    
    
     if(this.building[building].floors[floor].kitchen){
             this.building[building].floors[floor].section_cost=this.building[building].floors[floor].size.cost
              for(var k=0;k<this.building[building].floors[floor].kitchens.length;k++){
                  this.building[building].floors[floor].section_cost=this.building[building].floors[floor].section_cost+this.building[building].floors[floor].kitchens[k].size.cost
              }
          }

      for (var i = 0; i < this.billingData.length; i++) {
      if (
         this.billingData[i].name ==
        "Building " + (building + 1) + " Floor " + floor
      ) {
        
        this.billingData[i].section = this.building[building].floors[
          floor - 1
        ];
      }
    }
    this.findTempcost()
    this.calcTotal()

  },
  calcTotal(){
    console.log("i m inside total cost ")
      this.totalCost = 0;
      
      for (var i = 0; i < this.multiServicesBill.length; i++) {
        for(var j=0;j<this.multiServicesBill[i].bill.length;j++)
        {
          /*if(!this.multiServicesBill[i].bill[j].section.kitchen)
          {
                        this.multiServicesBill[i].bill[j].section.section_cost=this.multiServicesBill[i].bill[j].section.size.cost
                        this.multiServicesBill[i].bill[j].section.section_net_cost=this.multiServicesBill[i].bill[j].section.size.cost
          }*/
      this.totalCost = this.totalCost + this.multiServicesBill[i].bill[j].section_net_cost;
        }
    }
    console.log("i m inside total cost and it is "+this.totalCost)
  },
   recalcApartmentPrice(building,floor,apartment) {
    /*this.totalCost = 0;
    for (var i = 0; i < this.billingData.length; i++) {
      this.totalCost = this.totalCost + this.billingData[i].section.size.cost;
    }*/
     if(this.building[building].floors[floor].apartments[apartment].kitchen){
             this.building[building].floors[floor].apartments[apartment].section_cost=this.building[building].floors[floor].apartments[apartment].size.cost
              for(var k=0;k<this.building[building].floors[floor].apartments[apartment].kitchens.length;k++){
                  this.building[building].floors[floor].apartments[apartment].section_cost=this.building[building].floors[floor].apartments[apartment].section_cost+this.building[building].floors[floor].apartments[apartment].kitchens[k].size.cost
              }
          }
     var apartmentFound = false;
    for (var i = 0; i < this.billingData.length; i++) {
      if (
        this.billingData[i].name ==
        "Building " + (building + 1) + " Floor " + (floor+1)+ " Apartment " + (apartment+1)
      ) {
        apartmentFound = true;
        
        this.billingData[i].section = this.building[building].floors[
          floor
        ].apartments[apartment];

      }
    }
  
     this.calcTotal()
 this.findTempcost()
  },
  setCost(building, floor, apartment) {
    this.building[building].floors[floor].apartments[apartment].cost = "";
  },
 getKitchenProductivity(){
  axios
  .get(
    this.url+"/customer/ajax/getserviceproductivity?service_type=" +
      'Kitchen Cleaning'
  ).then(response=>{
    this.new_kitchen_cabinet_productivity=  response.data.newkitchenwithcabinet_perhour_cleaning
    this.new_kitchen_nocabinet_productivity=  response.data.newkitchenwithout_perhour_cleaning
    this.old_kitchen_cabinet_productivity=  response.data.oldkitchenwithcabinet_perhour_cleaning
    this.old_kitchen_nocabinet_productivity=  response.data.oldkitchenwithoutcabinet_perhour_cleaning
  })
 },
  doSomethingAsync(k) {
   return new Promise((resolve) => {
     if(this.schedule_serviceTypes[k]=='Kitchen Appliances'){
      var service_to_select='Kitchen Cleaning'
     }
     else{
     var service_to_select=this.schedule_serviceTypes[k]
     }
       axios
      .get(
        this.url+"/customer/ajax/getserviceproductivity?service_type=" +
        service_to_select
      )
      .then((response) => {
        var total_highpricewindow_size = 0;
        var total_lowpricewindow_size = 0;
        var total_highpricefacade_size = 0;
          var total_lowpricefacade_size = 0;
           var selected_service=this.schedule_serviceTypes[k]
          console.log(response.data)
          this.durationData[this.schedule_serviceTypes[k]]=response.data

          /*   Calculation begins */
         console.log("selected service is"+selected_service)
      

          var data = response.data;
        console.log(data);
        //to find total size and manhour
        if (selected_service == "Upholstery Cleaning") {
          var total_sofa_size = this.sofa_size;
          var total_chair_size = this.chair_size;
         // var total_curtain_size = 750;
          var manhour =
            parseInt(total_sofa_size / data["sofa_perhour_cleaning"]) +
            parseInt(total_chair_size / data["chair_perhour_cleaning"]);
            console.log("up manhour is "+manhour)
        } else if (selected_service == "Facade Cleaning") {
          for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
            if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.is_highprice_facade){
              total_highpricefacade_size=total_highpricefacade_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
            }
            else{
              total_lowpricefacade_size=total_lowpricefacade_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
            }
          }
          var manhour =
            parseInt(
              total_highpricefacade_size /
                data["highpricefacade_perhour_cleaning"]
            ) +
            parseInt(
              total_lowpricefacade_size /
                data["lowpricefacade_perhour_cleaning"]
            );
        } else if (selected_service == "Kitchen Cleaning") {
          
          var manhour =
            parseInt(
              this.new_kitchen_cabinet_size / data["newkitchenwithcabinet_perhour_cleaning"]
            ) +
            parseInt(
              this.new_kitchen_nocabinet_size / data["newkitchenwithout_perhour_cleaning"]
            )+
            parseInt(
              this.old_kitchen_cabinet_size / data["oldkitchenwithcabinet_perhour_cleaning"]
            )+
            parseInt(
              this.old_kitchen_nocabinet_size / data["oldkitchenwithoutcabinet_perhour_cleaning"]
            )
            //To find addons man hour 
            var addon_manhour=0
            for(var ao=0;ao<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;ao++){
                for(var addon=0;addon<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons.length;addon++){
                  if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].selected){
                    if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].details.category){
                      addon_manhour=addon_manhour+(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].quantity*(parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].selected_size.max_size)/this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].details.productivity))
                    }
                    else{
                    addon_manhour=addon_manhour+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].details.productivity*this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].quantity
                    }
                  }
                }
            
            }
            console.log("addon manhour is"+addon_manhour)
            manhour=parseInt(manhour)+parseInt(addon_manhour)
        }
        else if(selected_service =='Kitchen Appliances'){
          var addon_manhour=0
          for(var ao=0;ao<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;ao++){
            for(var addon=0;addon<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons.length;addon++){
              if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].selected){
                if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].details.category){
                  addon_manhour=addon_manhour+(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].quantity*(parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].selected_size.max_size)/this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].details.productivity))
                }
                else{
                addon_manhour=addon_manhour+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].details.productivity*this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addons[addon].quantity
                }
              }
            }
        
        }
        console.log("addon manhour is"+addon_manhour)
        var manhour=parseInt(addon_manhour)
        }
        
        else if (selected_service == "Window Cleaning") {
          for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
            if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.is_highprice_window){
              total_highpricewindow_size=total_highpricewindow_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
            }
            else{
              total_lowpricewindow_size=total_lowpricewindow_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.size.max_size
            }
          }
          
          var manhour =
            parseInt(
              total_highpricewindow_size /
                data["highpricewindow_perhour_cleaning"]
            ) +
            parseInt(
              total_lowpricewindow_size /
                data["lowpricewindow_perhour_cleaning"]
            );
        } else {
          var total_estimated_size = this.total_size;
          var productivity = data["perhour_cleaning"];
          console.log("productivity is "+productivity)
          var manhour = parseInt(total_estimated_size / productivity);
          var new_kit_cab_size=0
          var new_kit_nocab_size=0
          var old_kit_cab_size=0
          var old_kit_nocab_size=0
          var kit_manhour=0
          for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
          if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchen){
            for(var kit=0;kit<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens.length;kit++){
              if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].is_newkitchen){
                if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].is_cabinet){
                  new_kit_cab_size=new_kit_cab_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                }
                else{
                  new_kit_nocab_size=new_kit_nocab_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                }
               
              }else{
                if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].is_cabinet){
                old_kit_cab_size=old_kit_cab_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                }
                else{
                  old_kit_nocab_size=old_kit_nocab_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].section.kitchens[kit].size.max_size
                }
              }
            }
          }
          }
          kit_manhour=parseInt(new_kit_cab_size/this.new_kitchen_cabinet_productivity)+parseInt(old_kit_cab_size/this.old_kitchen_cabinet_productivity)
          +parseInt(old_kit_nocab_size/this.old_kitchen_nocabinet_productivity)+parseInt(new_kit_nocab_size/this.new_kitchen_nocabinet_productivity)
          manhour=manhour+kit_manhour
        }
        if(manhour<2){
          manhour=2
        }
        console.log("size estimated is" + total_estimated_size);
         console.log("sofa size estimated is" + total_sofa_size);
           console.log("chair size estimated is" + total_chair_size)
           console.log("manhour  estimated is" + manhour);
        //optimal finding
        this.totalmanhour=this.totalmanhour+manhour
        console.log("total man hour is "+this.totalmanhour)
        var r = 2 ** (this.totalmanhour.toString().length + 1);
        var mod = this.totalmanhour % r;

        if (mod > parseInt(r / 4)) {
            this.n = this.totalmanhour + (r - mod);
        } else {
           this.n = this.totalmanhour - mod;
        }
        console.log(manhour, "manhour");
        console.log(r, "r");
        console.log(mod, "mod");
        console.log(this.n, "n");
         
        this.maxCleaners.push(response.data.max_cleaners)
       resolve("done")
       
       
      }).catch((error) => {
        console.log(error);
      })
   });
 },
  newdurationcalculation(){
     this.duration=[]
     this.totalmanhour=0
  let promises = [];
  var count=0;
     for(var k=0;k<this.schedule_serviceTypes.length;k++){
      
     
  promises.push(
    this.doSomethingAsync(k)    
    )
    
    
    }
    /** Loop ends here  */
    Promise.all(promises)
.then(responses =>{
  console.log("i am ready")
    var manhour=this.totalmanhour
    var n=this.n
    console.log("n is "+n)
    console.log("man hour  is "+manhour)
    var pair = [];
        for (var i = 1; i < parseInt(n ** (1 / 2)) + 1; i++) {
          if (n % i == 0) {
            pair = [i, n / i];
          }
        }
        console.log(pair, "pair");
        //pair convert to 3's multiple
        var convertion_r = 2;
        var convertion_mod = pair[1] % convertion_r;
        var highest_cleaner=Math.max(...this.maxCleaners)
        var lowest_cleaner=Math.min(...this.maxCleaners)

        if (convertion_mod > parseInt(convertion_r / 2)) {
          console.log(manhour, "divider");
          console.log(pair[1] + (convertion_r - convertion_mod), "divident");
          console.log(
            parseInt(manhour / (pair[1] + (convertion_r - convertion_mod))),
            "division"
          );
          pair = [
            Math.round(manhour / (pair[1] + (convertion_r - convertion_mod))),
            pair[1] + (convertion_r - convertion_mod),
          ];
        } else {
          console.log(manhour, "divider");
          console.log(pair[1] - convertion_mod, "divident");

          if (pair[1] - convertion_mod == 0) {
            pair = [Math.round(manhour / 2), 2];
          } else {
            pair = [
              Math.round(manhour / (pair[1] - convertion_mod)),
              pair[1] - convertion_mod,
            ];
          }
        }

        console.log(pair, "newpair");

        //var max_cleaners = data["max_cleaners"];
        //max_cleaners=10;
        console.log("lowest cleaner is "+lowest_cleaner)
        var duration_list = [];
        var lower_loop = 0;
        var upper_loop = 0;
        var middle_element = pair[0];
        var middle_hours = pair[1];

        if (middle_element <= lowest_cleaner && middle_element > 0) {
          duration_list.push(pair);

          //first
          if (
            Math.round(manhour / (middle_hours - 2)) > 0 &&
            Math.round(manhour / (middle_hours - 2)) <= lowest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours - 2)),
              middle_hours - 2,
            ]);
            lower_loop = 1;
          }
          if (
            Math.round(manhour / (middle_hours + 2)) > 0 &&
            Math.round(manhour / (middle_hours + 2)) <= lowest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 2)),
              middle_hours + 2,
            ]);
            upper_loop = 1;
          }

          //check
          if (
            Math.round(manhour / (middle_hours - 4)) > 0 &&
            Math.round(manhour / (middle_hours - 4)) <= lowest_cleaner &&
            upper_loop == 0
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours - 4)),
              middle_hours - 4,
            ]);
            lower_loop = 1;
          }
          if (
            Math.round(manhour / (middle_hours + 4)) > 0 &&
            Math.round(manhour / (middle_hours + 4)) <= lowest_cleaner &&
            lower_loop == 0
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 4)),
              middle_hours + 4,
            ]);
            upper_loop = 1;
          }
        } else if (middle_element == 0 && lowest_cleaner > 0) {
          //1st
          duration_list.push([1, middle_hours]);

          //2nd
          if (
            Math.round(manhour / (middle_hours + 2)) > 0 &&
            Math.round(manhour / (middle_hours + 2)) <= lowest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 2)),
              middle_hours + 2,
            ]);
          } else {
            duration_list.push([1, middle_hours + 2]);
          }

          //3rd
          if (
            Math.round(manhour / (middle_hours + 4)) > 0 &&
            Math.round(manhour / (middle_hours + 4)) <= lowest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 4)),
              middle_hours + 4,
            ]);
          } else {
            duration_list.push([1, middle_hours + 4]);
          }
        } else {
          middle_element = lowest_cleaner;
          middle_hours =
            Math.round(manhour / middle_element) -
            (Math.round(manhour / middle_element) % 2);
          if (middle_hours == 0) {
            middle_hours = 2;
          }

          //1st
          duration_list.push([middle_element, middle_hours]);

          //2nd
          if (
            Math.round(manhour / (middle_hours + 2)) > 0 &&
            Math.round(manhour / (middle_hours + 2)) <= lowest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 2)),
              middle_hours + 2,
            ]);
          } else {
            duration_list.push([middle_element, middle_hours + 2]);
          }

          //3rd
          if (
            Math.round(manhour / (middle_hours + 4)) > 0 &&
            Math.round(manhour / (middle_hours + 2)) <= highest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 4)),
              middle_hours + 4,
            ]);
          } else {
            duration_list.push([middle_element, middle_hours + 4]);
          }
        }
        console.log(duration_list);

        for (i = 0; i < duration_list.length; i++) {
          var total_duration = duration_list[i][1];
          //show to users
          var total_minutes = (total_duration.toFixed(2) * 60).toFixed(0);
          var converted_hours = Math.floor(total_minutes / 60);
          var converted_minutes = total_minutes % 60;
          var total_cleaners = duration_list[i][0];
          console.log(converted_hours, "converted_hours");
          console.log(converted_minutes, "converted_minutes");
          console.log(total_cleaners, "total_cleaners");
          this.setDuration(converted_hours, total_cleaners);
        }
        this.sortDuration()
})
  },
  durationcalculation() {
    
    this.duration=[]
    var selected_service = "General Cleaning";
    axios
      .get(
        this.url+"/customer/ajax/getserviceproductivity?service_type=" +
          selected_service
      )
      .then((response) => {
        var data = response.data;
        console.log(data);
        //to find total size and manhour
        if (selected_service == "Upholstery Cleaning") {
          var total_sofa_size = 6;
          var total_chair_size = 9;
          var total_curtain_size = 750;
          var manhour =
            parseInt(total_sofa_size / data["sofa_perhour_cleaning"]) +
            parseInt(total_chair_size / data["chair_perhour_cleaning"]) +
            parseInt(total_curtain_size / data["curtain_perhour_cleaning"]);
        } else if (selected_service == "Facade Cleaning") {
          var total_highpricefacade_size = 400;
          var total_lowpricefacade_size = 400;
          var manhour =
            parseInt(
              total_highpricefacade_size /
                data["highpricefacade_perhour_cleaning"]
            ) +
            parseInt(
              total_lowpricefacade_size /
                data["lowpricefacade_perhour_cleaning"]
            );
        } else if (selected_service == "Kitchen Cleaning") {
          var total_newkitchen_size = 400;
          var total_oldkitchen_size = 400;
          var manhour =
            parseInt(
              total_newkitchen_size / data["newkitchen_perhour_cleaning"]
            ) +
            parseInt(
              total_oldkitchen_size / data["oldkitchen_perhour_cleaning"]
            );
        } else if (selected_service == "Window Cleaning") {
          var total_highpricewindow_size = 400;
          var total_lowpricewindow_size = 400;
          var manhour =
            parseInt(
              total_highpricewindow_size /
                data["highpricewindow_perhour_cleaning"]
            ) +
            parseInt(
              total_lowpricewindow_size /
                data["lowpricewindow_perhour_cleaning"]
            );
        } else {
          var total_estimated_size = this.total_size;
          var productivity = data["perhour_cleaning"];
          var manhour = parseInt(total_estimated_size / productivity);
        }
        console.log("size estimated is" + total_estimated_size);
        //optimal finding
        var r = 2 ** (manhour.toString().length - 1);
        var mod = manhour % r;

        if (mod > parseInt(r / 2)) {
          var n = manhour + (r - mod);
        } else {
          var n = manhour - mod;
        }
        console.log(manhour, "manhour");
        console.log(r, "r");
        console.log(mod, "mod");
        console.log(n, "n");
        var pair = [];
        for (var i = 1; i < parseInt(n ** (1 / 2)) + 1; i++) {
          if (n % i == 0) {
            pair = [i, n / i];
          }
        }
        console.log(pair, "pair");
        //pair convert to 3's multiple
        var convertion_r = 3;
        var convertion_mod = pair[1] % convertion_r;

        if (convertion_mod > parseInt(convertion_r / 3)) {
          console.log(manhour, "divider");
          console.log(pair[1] + (convertion_r - convertion_mod), "divident");
          console.log(
            parseInt(manhour / (pair[1] + (convertion_r - convertion_mod))),
            "division"
          );
          pair = [
            Math.round(manhour / (pair[1] + (convertion_r - convertion_mod))),
            pair[1] + (convertion_r - convertion_mod),
          ];
        } else {
          console.log(manhour, "divider");
          console.log(pair[1] - convertion_mod, "divident");

          if (pair[1] - convertion_mod == 0) {
            pair = [Math.round(manhour / 3), 3];
          } else {
            pair = [
              Math.round(manhour / (pair[1] - convertion_mod)),
              pair[1] - convertion_mod,
            ];
          }
        }

        console.log(pair, "newpair");

        var max_cleaners = data["max_cleaners"];
        //max_cleaners=10;
        var duration_list = [];
        var lower_loop = 0;
        var upper_loop = 0;
        var middle_element = pair[0];
        var middle_hours = pair[1];

        if (middle_element <= max_cleaners && middle_element > 0) {
          duration_list.push(pair);

          //first
          if (
            Math.round(manhour / (middle_hours - 3)) > 0 &&
            Math.round(manhour / (middle_hours - 3)) <= max_cleaners
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours - 3)),
              middle_hours - 3,
            ]);
            lower_loop = 1;
          }
          if (
            Math.round(manhour / (middle_hours + 3)) > 0 &&
            Math.round(manhour / (middle_hours + 3)) <= max_cleaners
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 3)),
              middle_hours + 3,
            ]);
            upper_loop = 1;
          }

          //check
          if (
            Math.round(manhour / (middle_hours - 6)) > 0 &&
            Math.round(manhour / (middle_hours - 6)) <= max_cleaners &&
            upper_loop == 0
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours - 6)),
              middle_hours - 6,
            ]);
            lower_loop = 1;
          }
          if (
            Math.round(manhour / (middle_hours + 6)) > 0 &&
            Math.round(manhour / (middle_hours + 6)) <= max_cleaners &&
            lower_loop == 0
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 6)),
              middle_hours + 6,
            ]);
            upper_loop = 1;
          }
        } else if (middle_element == 0 && max_cleaners > 0) {
          //1st
          duration_list.push([1, middle_hours]);

          //2nd
          if (
            Math.round(manhour / (middle_hours + 3)) > 0 &&
            Math.round(manhour / (middle_hours + 3)) <= max_cleaners
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 3)),
              middle_hours + 3,
            ]);
          } else {
            duration_list.push([1, middle_hours + 3]);
          }

          //3rd
          if (
            Math.round(manhour / (middle_hours + 6)) > 0 &&
            Math.round(manhour / (middle_hours + 6)) <= max_cleaners
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 6)),
              middle_hours + 6,
            ]);
          } else {
            duration_list.push([1, middle_hours + 6]);
          }
        } else {
          middle_element = max_cleaners;
          middle_hours =
            Math.round(manhour / middle_element) -
            (Math.round(manhour / middle_element) % 3);
          if (middle_hours == 0) {
            middle_hours = 3;
          }

          //1st
          duration_list.push([middle_element, middle_hours]);

          //2nd
          if (
            Math.round(manhour / (middle_hours + 3)) > 0 &&
            Math.round(manhour / (middle_hours + 3)) <= max_cleaners
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 3)),
              middle_hours + 3,
            ]);
          } else {
            duration_list.push([middle_element, middle_hours + 3]);
          }

          //3rd
          if (
            Math.round(manhour / (middle_hours + 6)) > 0 &&
            Math.round(manhour / (middle_hours + 3)) <= max_cleaners
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 6)),
              middle_hours + 6,
            ]);
          } else {
            duration_list.push([middle_element, middle_hours + 6]);
          }
        }
        console.log(duration_list);

        for (i = 0; i < duration_list.length; i++) {
          var total_duration = duration_list[i][1];
          //show to users
          var total_minutes = (total_duration.toFixed(2) * 60).toFixed(0);
          var converted_hours = Math.floor(total_minutes / 60);
          var converted_minutes = total_minutes % 60;
          var total_cleaners = duration_list[i][0];
          console.log(converted_hours, "converted_hours");
          console.log(converted_minutes, "converted_minutes");
          console.log(total_cleaners, "total_cleaners");
          this.setDuration(converted_hours, total_cleaners);
        }
      })
      .catch((error) => {
        console.log(error);
      });
  },
},
mounted() {
  this.url = api;
 // this.getAddons()
  this.getServices()
  this.getKitchenProductivity()
  this.getAreaTypes()
  this.getIp()
  this.getGovernorate()
  console.log("current time is" + moment().format());

  this.dateSelected = moment().format().split("T")[0];
  this.today = moment().format().split("T")[0];
  this.oneTimeDateSelected=moment().format().split("T")[0];
  this.one_time_slots[this.oneTimeDateSelected]={
    slots:[]
  }
  this.formatDate();
      this.getMultipleSlots()
     
      this.changeNewKitchen()

  this.selectCategory('Detailed Cleaning')
  
  //moment.tz.setDefault("Asia/Baghdad");
  
     
      
},
created()
{
  
},
    
   
   
  });
  
  




