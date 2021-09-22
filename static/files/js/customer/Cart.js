moment.locale('ar-kw');  
function openNav() {
  document.getElementById("mobSidenav").style.width = "100%";
  document.getElementById("mobSidenav").style.zIndex="1000";
}

function closeNav() {
  document.getElementById("mobSidenav").style.width = "0";
}  
function toggleBanner(){
    if($(".banner-left").is(":visible") ){
      showBanner()
    }
    else{
      hideBanner()
    }
}


function checkSecond(sec) {
  if (sec < 10 && sec >= 0) {sec = "0" + sec}; // add zero in front of numbers < 10
  if (sec < 0) {sec = "59"};
  return sec;
}
function hideBanner(){
  $('.banner-container').css("width","0px")
  $('.banner-box').hide()
  $(".banner-left").show()
  $(".banner-right").hide()
}
function showBanner(){
  $('.banner-container').css("width","195px")
  $('.banner-box').show()
  $(".banner-left").hide()
  $(".banner-right").show()
}

$(document).ready(function(){
    $('#category-carousel').owlCarousel({
      loop:false,
      
      responsiveClass:true,
      responsive:{
          0:{
              items:1,
              nav:true
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
      responsive:{
          0:{
              items:1,
              nav:true,
              loop:true
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

  
  
  
  
  });
  
  
  
  const app=new Vue({
      el: '#app',
      delimiters: ['<%', '%>'],
      vuetify: new Vuetify({theme: {
          themes: {
            light: {
              primary: '#289bac', // #E53935
              secondary: '#FFCDD2', // #FFCDD2
              accent: '#3F51B5', // #3F51B5
            },
          },
        }}),
        components:{
          
        },
      data: {
        addons:[],
        order_no:'',
        counterTime:'',
        booking_time:'',
        checkbox:false,
        duration_loader:false,
        pref_gender:false,
        btnLoader:false,
        settings:{},
        booking_status:false,
       // success_booking_dialog:true,
       gender_pref:false,
       gender:" ",
        slot_loader:false,
        payment_total_cost:0,
        payable_amount:0,
        customDateSelected:[],
        customDialog:false,
        cleaningPolicy:'One Time',
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
     
      customer_id:null,
      address_id:null,
      service_details:{},
      schedule_details:{},
      address_details:{
      "governorate":null,
      "area":null,
      "block":null,
      "avenue":"",
      "building":"",
      "street":"",
      "floor":null,
      "apartment":""
   },
      customer_details:{
        "name":"",
      "gender":"",
      "email":"",
      "mobile_number":"",
      "date_day":null,
      "date_month":null,
      "date_year":null,
      "nationality":"",
      "sms_preference":"",
      "contact_platform":""
      }
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
     
      selectedCategory:'Detailed Cleaning',
    name: '',
    rules: {
      required: v => !!v || 'this field is required',
    },
      url:'',
      kitchenData:{
          wall_type:'',
          floor_type:'',
          size:'',
          ceiling_type:'',
          condition:'',
          type:'old',
          residue:false
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
    activeTab: "Cart",
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
    currentItem: "",
    service: "test",
    dialog: false,
    dialogmsg: "",
    otherServices: [],
    otherService:{
      material: "",
  
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
      hallway_size: "",
      sides: "",
      stain_age: "",
      height:""
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
    durationData:{},
    billSample:{
      name:'',
      section:{},
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
    new_kitchen_size:0,
    old_kitchen_size:0,
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
  schedule_confirmation_dialog:false,
  schedule_warning:false,
  payment_dialog:false,
  lastElem:1,
      subItemSelected:'',
      differentSlider:'engDifferent',
      testimonialSlider:'engTestimonial',
    activeWebTab:false,
    selectedTab:'',
    activeItem:'',
    category:'',
    serviceType:'',
    activeService:'',
    lang:'en',
    arabic:false,
    selectedBooking:'Cleaning',
    custId:'',
    gotData:false,
    bookingServicesBill:[],
    bookingonetimeslots:[],
    onetimeslots:[],
    multiAddress:false,
    selectedAddress:'',
    bookedServiceDetails:[],
    custServiceScheduled:{},
    currentAddressIndex:null,
    completedAddress:[],
    scheduleGroup:{},
    editScheduleData:{},
    editScheduleStat:false,
    evaluation_id:'',
    eval_details:{},
    payment_status:'',
    discount:false,
    discount_val:0,
    amount_discount:0,
    amount_payable:0,
    amount_subtotal:0
        },
     
/* header data */


        methods: {
          check: function(e) {
            e.cancelBubble = true;
            console.log('checkbox checked')
          },
          expansionPanel: function() {
            console.log('expansion panel')
          },
          resetGender(){
            this.gender=""
            this.getMultipleSlots()
          },
          closePaymentDialog(){
            this.payment_dialog=false
            location.reload()
          },
          checkSlotSelection(){
            for(var i in  this.one_time_slots){
              if(this.one_time_slots[i].slots.length>0){
                return true
              
              }
              
            }
            return false
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
          paymentSubmit(){
            if(this.activePayment=='debit'){
              $('#payment_submit').click()
            }
            else{
            /* window.location.href="https://testpay.bleach-kw.com/creditcard/payment_form.php?merchant_defined_data1={{order.order_no}}&reference_number={{order.order_no}}1&amount={{order.evaluation.before_cleaning_amount}}&merchant_defined_data2=prepaid&merchant_defined_data3={{order.order_status}}&currency=KWD&transaction_type=sale&bill_to_forename={{firstname}}&bill_to_surname={{lastname}}&bill_to_phone={{orderschedule.customer_address.customer.mobile_number}}&bill_to_email={{orderschedule.customer_address.customer.email}}&bill_to_address_country={{orderschedule.customer_address.customer.nationality.code}}&bill_to_address_city={{orderschedule.customer_address.area.name|default_if_none:''}}&bill_to_address_line1={{orderschedule.customer_address.governorate.name|default_if_none:''}}&merchant_defined_data4=

             ONLINE
             &merchant_defined_data5=NO&merchant_defined_data7=1&merchant_defined_data20=NO&customer_ip_address={{customer_ip_address}}"*/
             window.location.href="https://testpay.bleach-kw.com/creditcard/payment_form.php?merchant_defined_data1="+this.eval_details.order_no+"&reference_number="+this.eval_details.order_no+"1&amount="+this.payable_amount+"&merchant_defined_data2=prepaid&merchant_defined_data3="+this.eval_details.order_status+"currency=KWD&transaction_type=sale&bill_to_forename="+this.bookedServiceDetails[0].address.customer.name.split(" ")[1]+"&bill_to_surname="+this.bookedServiceDetails[0].address.customer.name.split(" ")[2]+"&bill_to_phone="+this.bookedServiceDetails[0].address.customer.mobile_number+"&bill_to_email="+this.bookedServiceDetails[0].address.customer.email+"&bill_to_address_country=KW"+"&bill_to_address_city="+this.bookedServiceDetails[0].address.area.name+"&bill_to_address_line1="+this.bookedServiceDetails[0].address.governorate.name+"&merchant_defined_data4=ONLINE&merchant_defined_data5=NO&merchant_defined_data7=1&merchant_defined_data20=NO&customer_ip_address="+this.ip_address
            }
           
          },
          viewEditSchedule(service,index){
            this.schedule_serviceTypes_selected=[]
            this.editScheduleData=service
            this.editScheduleStat=true
            this.schedule_serviceTypes_selected.push(index)
           
            this.goToSchedule()
          },
           getCustBookings(){

           },
            goToPaymentDialog(){
              
                this.selectPayment('debit')
                this.payment_dialog=true
            },
            goToScheduleConf(){
                if(this.scheduleStat && this.scheduleChecker()){
                   // this.schedule_confirmation_dialog=true
                   this.schedule_warning=true
                }
                else{
                    this.goToSchedule()
                }
            },
            dummyDataGenerator(num){
                this.billingData={
                    
                name:"Building 1 Floor 1",
                section:{
                apartment:false,
                apartments:[],
                ceiling_type:['WOODEN'],
                cement_residue:false,
                completed:true,
                floor_type:['MARBLE'],
                keynote_data:[],
                keynotes:{},
                kitchen:false,
                kitchens:[],
                no_of_bathrooms:"3",
                no_of_rooms:"2",
                no_of_windows:"4",
                paint_residue:false,
                section_cost:190,
                section_name:"",
                section_net_cost:"",
                size:{
                    combinedSize:"Medium( 51 sq. m - 100 sq. m )",
                    cost:190,
                    max_size:100,
                    min_size:51,
                    name:"Medium",
                },
                upholsteries:[],
                wall_type:["BRICKS"]

                }
            }
            for(var i=0;i<num;i++){
                this.multiServicesBill.push({
                    area_type:"APARTMENT",
                    bill:[],
                    
                    evaluator_note:"wdwdwd",
                    location_type:"Fully Furnished",
                    service:"General Cleaning",
                    serviceNo:1 ,
                    total_cost:190,
                    schedule_details:{}
                })
                this.multiServicesBill[this.multiServicesBill.length-1].bill.push(this.billingData)
            }
        },
        scheduleStatChecker(){
            var flag=false
            for(var i=0;i<this.multiServicesBill.length;i++){
                if(Object.keys(this.multiServicesBill[i].schedule_details).length<1){
                    flag=false;
                    break
                }
                else {
                    flag=true
                }
            }
            return flag
        },
        scheduleChecker(){
            var flag=false
            for(var i=0;i<this.multiServicesBill.length;i++){
                if(Object.keys(this.multiServicesBill[i].schedule_details).length>0){
                    flag=true;
                    break
                }
                else {
                    flag=false
                }
            }
            return flag
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
            
            this.getMultipleSlots()
          },
          resetScheduler(){
            this.oneTimeSelectionStat=false
              this.editScheduleStat=false
            this.cleaningPolicy='',
            this.subStat='',
            this.visits=[],
            this.fixedSlots={},
            this.altdaysStat=false,
            this.altweekStat=false,
            this.selected_double_slots=[],
            this.selected_monthly_date=[],
            this.autofixStat=false,
            this.selected_monthly_date=[],
            this.reselectDialog=false,
            this.reselectSlot=[],
            this.reselectDate={},
            this.reselectDateIndex=null,
            this.scheduleFormat={
              allSchedule:{},
              individual:{}
            },
            this.no_of_visits='',
            this.scheduleDateSat=false
            this.confirmation_dialog=false
            this.monthly_starting_date=''
            this.customDateSelected=[]
            this.selectedDuration={
              cleaners:null,
              hours:null,
              slots:null
            },
            this.schedule_err_msg=false
  
          },
          addKeynote(building,floor){
            this.building[building].floors[floor].keynote_data.push({
              name:this.keynote_name,
              value:this.keynote_value
            })
            this.keynote_name=''
            this.keynote_value=''
          },
          removeKeynote(building,floor,keynote){
              this.building[building].floors[floor].keynote_data.splice(keynote,1)
          },
          addApartmentKeynote(building,floor,apartment){
            this.building[building].floors[floor].apartments[apartment].keynote_data.push({
              name:this.keynote_name,
              value:this.keynote_value
            })
            this.keynote_name=''
            this.keynote_value=''
          },
          removeApartmentKeynote(building,floor,apartment,keynote){
              this.building[building].floors[floor].apartments[apartment].keynote_data.splice(keynote,1)
          },
          calcSelectedServices(){
            this.schedule_serviceTypes=[]
            
              for(var i=0;i<this.schedule_serviceTypes_selected.length;i++){
                this.schedule_serviceTypes.push(this.multiServicesBill[this.schedule_serviceTypes_selected[i]].service)
              }
            
          },
          addScheduledService(service,index){
            this.schedule_serviceTypes_selected[index]={
              service:service
            }
          },
          addOneTimeToSchedule(){
            
            
              for(var j=0;j<this.schedule_serviceTypes_selected.length;j++){
                this.onetime_scheduled[this.schedule_serviceTypes_selected[j]]={
                  slot:this.selected_onetime_slots
                }
              }
            
            for(var j=0;j<this.schedule_serviceTypes_selected.length;j++){
              this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaning_policy='ONE TIME SERVICE'
              this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details={}
              var count=0
              if(this.discount && this.payment_status=='PENDING'){
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].discount=this.discount
               }
              for(var k in this.selected_onetime_slots){
                var yr=k.split('-')[0]
                var month=k.split('-')[1]
                var day=k.split('-')[2]
                var date=day+'-'+month+'-'+yr
                var min_slot=Math.min(...this.selected_onetime_slots[k].slots)
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[count+1]={
                  
                  "date":date,
                 "time":this.slotFormat[min_slot].start_time,
                "no_of_cleaners":this.selectedDuration.cleaners,
                 "cleaning_hours":this.selected_onetime_slots[k].slots.length*2
                }
                count=count+1
              }
            }
            for(var k=0;k<this.schedule_serviceTypes_selected;k++)
            {
              for(var sch in this.scheduleGroup){
                
               if(this.scheduleGroup[sch].includes(this.schedule_serviceTypes_selected[k])){
                 var index=this.scheduleGroup[sch].indexOf(this.schedule_serviceTypes_selected[k])
                 console.log("index is"+index)
                 this.scheduleGroup[sch].splice(index,1)
               }
               }
              }
              var groundid=Object.keys(this.scheduleGroup).length
              this.scheduleGroup[groundid]=[ ...this.schedule_serviceTypes_selected ]
            this.selected_onetime_slots={}
            this.onetime_scheduled={}
            this.oneTimeSelectionStat=false
            this.schedule_serviceTypes_selected=[]
           // this.oneTimeDateSelected=''
           //this.one_time_slots={}
           
            this.activeTab='Cart'
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
            
            
              for(var i=0;i<this.schedule_serviceTypes_selected.length;i++){
                
                this.scheduleFormat.individual[this.schedule_serviceTypes_selected[i]]={
                  starting_date:this.visits[0].dateTime,
                  visits:this.visits
                }
                
              }
            
            for(var j=0;j<this.schedule_serviceTypes_selected.length;j++){
              this.multiServicesBill[this.schedule_serviceTypes_selected[j]].cleaning_policy='SUBSCRIPTION'
              this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details={}
              for(var k=0;k<this.visits.length;k++){
                var min_slot=Math.min(...this.visits[k].slots)
                
                this.multiServicesBill[this.schedule_serviceTypes_selected[j]].schedule_details[k+1]={
                  
                  "date":this.visits[k].date,
                 "time":this.slotFormat[min_slot].start_time,
                "no_of_cleaners":this.selectedDuration.cleaners,
                 "cleaning_hours":this.visits[k].slots.length*2
                }
              }
             
            }
  
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
            
            this.scheduleDateSat=false
            this.activeTab='Cart'
          },
          changeVisitDate(){
            
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
          findCustomVisits(){
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
            
          },
          findVisits(){
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
          },
          findMonthlyVisits(){
            if(this.selected_monthly_date.length>0 && this.selected_double_slots.length>0 )
            {
            console.log("called monthly")
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
             console.log("yes i foiund")
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
          },
          checkAvailablility(){
           axios.post(this.url+'/customer/ajax/multipleservice/multipledates/cleaningslotes/',{number_of_cleaners:this.selectedDuration.cleaners,
            cleaning_hours:this.selectedDuration.hours,
            service_types:this.schedule_serviceTypes,
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
      arrangeData(){
            for(var i=0;i<this.multiServicesBill.length;i++){
  
              var service_id=this.getServiceId(this.multiServicesBill[i].service)
               this.serviceDetails.service_details[i]={
                  "service_type":service_id,
                  "location_type":this.multiServicesBill[i].location_type,
                  "area_type":this.multiServicesBill[i].area_type,
                   "evaluator_note":this.multiServicesBill[i].evaluator_note,
                   "estimated_cost":this.multiServicesBill[i].total_cost,
                   "total_cost":this.multiServicesBill[i].total_cost,
                   "number_of_cleaners":this.selectedDuration.cleaners,
                     "cleaning_hours":parseInt(this.selectedDuration.hours),
                     sections:{}
                }
              for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
                
             if(this.multiServicesBill[i].bill[j].section.wall_type && this.multiServicesBill[i].bill[j].section.ceiling_type)
             {
               this.serviceDetails.service_details[i].sections[j]={
                 "section_name":this.multiServicesBill[i].bill[j].name,
               "size":this.multiServicesBill[i].bill[j].section.size.name,
               "wall_type":this.multiServicesBill[i].bill[j].section.wall_type.join(),
               "ceiling_type":this.multiServicesBill[i].bill[j].section.ceiling_type.join(),
               "cement_residue":this.multiServicesBill[i].bill[j].section.cement_residue,
               "section_cost":this.multiServicesBill[i].bill[j].section.section_cost,
               "section_net_cost":this.multiServicesBill[i].bill[j].section.section_cost,
               "keynotes":{
                  "1":{
                     "sub_area":"bathroom",
                     "quantity":this.multiServicesBill[i].bill[j].section.no_of_bathrooms
                  },
                  "2":{
                     "sub_area":"rooms",
                     "quantity":this.multiServicesBill[i].bill[j].section.no_of_rooms
                  },
                  "3":{
                     "sub_area":"windows",
                     "quantity":this.multiServicesBill[i].bill[j].section.no_of_windows
                  }
               }
               }
             }
             else{
               this.serviceDetails.service_details[i].sections[j]={
                 "section_name":this.multiServicesBill[i].bill[j].name,
               "size":this.multiServicesBill[i].bill[j].section.size.name,
               "wall_type":this.multiServicesBill[i].bill[j].section.wall_type,
               "ceiling_type":this.multiServicesBill[i].bill[j].section.ceiling_type,
               "cement_residue":this.multiServicesBill[i].bill[j].section.cement_residue,
               "section_cost":this.multiServicesBill[i].bill[j].section.section_cost,
               "section_net_cost":this.multiServicesBill[i].bill[j].section.section_cost,
               "keynotes":{
                  "1":{
                     "sub_area":"bathroom",
                     "quantity":this.multiServicesBill[i].bill[j].section.no_of_bathrooms
                  },
                  "2":{
                     "sub_area":"rooms",
                     "quantity":this.multiServicesBill[i].bill[j].section.no_of_rooms
                  },
                  "3":{
                     "sub_area":"windows",
                     "quantity":this.multiServicesBill[i].bill[j].section.no_of_windows
                  }
               }
               }
             }
              }
            }
            if(this.userStat)
            {
            this.serviceDetails.customer_details= {   
                "name":this.customerDetails.customer_details.name,
                "gender":this.customerDetails.customer_details.gender,
                 "email":this.customerDetails.customer_details.email,
               "mobile_number":this.customerDetails.customer_details.mobile_number,
               "date_day":this.customerDetails.customer_details.date_day,
              "date_month":this.customerDetails.customer_details.date_month,
             "date_year":this.customerDetails.customer_details.date_year,
              "nationality":this.customerDetails.customer_details.nationality,
               "sms_preference":this.customerDetails.customer_details.sms_preference,
            "contact_platform":''
            }
            this.serviceDetails.customer_id=this.customerDetails.customer_details.id
            this.serviceDetails.address_details={
                 governorate: this.selectedAddress.governorate.id,
                 area: this.selectedAddress.area.id,
                 block: this.selectedAddress.block,
                avenue: this.selectedAddress.avenue,
                building: this.selectedAddress.building,
                street: this.selectedAddress.street,
                 floor: this.selectedAddress.floor,
               apartment:this.selectedAddress.apartment,
            }
            this.serviceDetails.address_id=this.selectedAddress.id
            }
            else{
              this.serviceDetails.customer_details.contact_platform=this.contact_platform.join(',')
              this.serviceDetails.customer_details.date_day=this.dob.split('-')[2]
              this.serviceDetails.customer_details.date_month=this.dob.split('-')[1]
              this.serviceDetails.customer_details.date_year=this.dob.split('-')[0]
            }
            this.serviceDetails.total_cost=this.totalCost
            this.serviceDetails.estimated_cost=this.totalCost
            //this.customerDetails.customer_details
            //this.serviceDetails['customer_addresses']= this.customerDetails.customer_addresses
            this.bookMultipleService()
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
          type:'old',
          residue:false
      }
     this.recalcApartmentPrice(building,floor,apartment)
   
         
      },
        addMoreKitchen(building,floor){
        
          if(this.$refs['KitchenForm-building-'+building+'floor'-floor].validate())
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
          type:'old',
          residue:false
      }
      this.kitchendialog=false
      this.recalcPrice(building,floor)
         
      }
        },
      addMoreKitchenApartment(building,floor,apartment){
        
         
          console.log("kitchen data is  "+JSON.stringify(this.kitchenData))
          this.building[building].floors[floor].apartments[apartment].kitchens.push(this.kitchenData)
            this.forceRerender();
            this.kitchenData={
          wall_type:'',
          floor_type:'',
          size:'',
          ceiling_type:'',
          condition:'',
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
         
         
      },
      addNewApartmentKitchen(building,floor,apartment){
        
         this.kitchenType='apartment'
         this.currentBuilding=building
         this.currentFloor=floor
         this.currentApartment=apartment
          this.kitchendialog=true
          this.kitchendialogStat=true
         
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
      if (this.otherService.type == "new") {
        console.log("type test passed new");
        for (var i = 0; i < this.sizeData.length; i++) {
          if (this.sizeData[i].is_newkitchen) {
            this.sizeFilteredData.push(this.sizeData[i]);
          }
        }
      }
      if (this.otherService.type == "old") {
        console.log("type test passed old");
        for (var i = 0; i < this.sizeData.length; i++) {
          if (!this.sizeData[i].is_newkitchen) {
            this.sizeFilteredData.push(this.sizeData[i]);
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
        console.log("type test passed new");
        for (var i = 0; i < this.kitchenSizeData.length; i++) {
          if (this.kitchenSizeData[i].is_newkitchen) {
            this.sizeFilteredData.push(this.kitchenSizeData[i]);
          }
        }
      }
      if (this.kitchenData.type == "old") {
        console.log("type test passed old");
        for (var i = 0; i < this.kitchenSizeData.length; i++) {
          if (!this.kitchenSizeData[i].is_newkitchen) {
            this.sizeFilteredData.push(this.kitchenSizeData[i]);
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
      this.one_time_slots[this.oneTimeDateSelected].slots.push(slot)
      this.onetimerender=true
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
    oneTimeSlotCounter(){
      var counter=0
      for(var i in this.one_time_slots){
        counter=counter+this.one_time_slots[i].slots.length
      }
      return counter
    },
    checkOneTimeSlotStat(slot){
      var prevSlot=parseInt(slot)-1
      var nextSlot=parseInt(slot)+1
      var counter=0
      for(var i in this.one_time_slots){
        counter=counter+this.one_time_slots[i].slots.length
      }
      if(counter<this.selectedDuration.slots && this.one_time_slots[this.oneTimeDateSelected].slots.length<5)
      {
      if(this.one_time_slots[this.oneTimeDateSelected].slots.length>0)
      {
      if(slot==1){
        if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(nextSlot)){
          return true
        }
        else {
          return false
        }
      }
      else if(slot==12){
        if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(prevSlot)){
          return true
        }
        else {
          return false
        }
      }
      else{
        if(this.one_time_slots[this.oneTimeDateSelected].slots.includes(prevSlot)||this.one_time_slots[this.oneTimeDateSelected].slots.includes(nextSlot))
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
    functionEvents (date) {
      //const [,, day] = date.split('-')
      //if ([12, 17, 28].includes(parseInt(day, 10))) return true
     // if ([1, 19, 22].includes(parseInt(day, 10))) return ['red', '#00f']
   /*  var selected_dates=[]
     for(var i in this.one_time_slots){
       if(this.one_time_slots[i].slots.length>0){
        selected_dates.push(i)
       }
     }
     if(selected_dates.includes(moment(date,'YYYY-MM-DD').subtract(1,"days").format('YYYY-MM-DD'))){
      return true
     }
      return false
    },*/
    var flag=false
   
   // var nextDay2=moment(this.today,'YYYY-MM-DD').add(2,"days").format('YYYY-MM-DD')
   
    for(var i=1;i<=this.settings.duration;i++){
      var nextDay=moment(this.today,'YYYY-MM-DD').add(i,"days").format('YYYY-MM-DD')
      if(moment(date,'YYYY-MM-DD').format('YYYY-MM-DD')==nextDay||moment(date,'YYYY-MM-DD').format('YYYY-MM-DD')==this.today){
        flag=true
        break
      }
      else{
        flag=false
      }
    }
    /*if(moment(date,'YYYY-MM-DD').format('YYYY-MM-DD')==nextDay||moment(date,'YYYY-MM-DD').format('YYYY-MM-DD')==nextDay2||moment(date,'YYYY-MM-DD').format('YYYY-MM-DD')==this.today){
      return true
    }*/
   
      return flag
    
    
  },
    oneTimeSlotCounter(){
      var counter=0
      for(var i in this.one_time_slots){
        counter=counter+this.one_time_slots[i].slots.length
      }
      return counter
    },
    submitOneTimeSlots(){
      this.selected_onetime_slots={}
     
      
        for(var i in this.one_time_slots){
          if(this.one_time_slots[i].slots.length>0){
            this.selected_onetime_slots[i]={
              slots:this.one_time_slots[i].slots
            }
          }
        }
      
       this.checkDiscount()
       this.addOneTimeToSchedule()
      this.onetime_dialog=false
      this.oneTimeSelectionStat=true
    },
    checkDiscount(){
      if(this.payment_status=='PENDING'){
      var dates=Object.keys(this.one_time_slots)
      this.discount=false
      var flag=false
      for(var i=0;i<dates.length;i++){
      for(var j=1;j<=this.settings.duration;j++){
        var nextDay=moment(this.today,'YYYY-MM-DD').add(j,"days").format('YYYY-MM-DD')
        if(dates[i]==nextDay||dates[i]==this.today){
          flag=true
          break
        }
        else{
          flag=false
        }
      }
    }
    if(flag){
      this.discount=true
    }
    else{
      this.discount=false
    }
  }
  else{
    return false
  }
    },
    calculateDiscount(){
      var discount=0
      for(var i=0;i<this.multiServicesBill.length;i++){
        if(this.multiServicesBill[i].discount){
          discount=discount+((this.settings.discount_percentage/100)*this.multiServicesBill[i].total_cost)
        }
      }
      return discount
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
                    this.old_kitchen_size=this.old_kitchen_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
                  }
                  if(this.multiServicesBill[j].bill[i].section.type=='new'){
                    this.new_kitchen_size=this.new_kitchen_size+ parseInt(this.multiServicesBill[j].bill[i].section.size.max_size)
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
    
      this.otherServices = [];
     this.billingData=[];
      this.building = [];
      this.no_of_building = 0;
      this.no_of_floors = [];
      this.no_of_apartments = [];
      this.buildingsCompleted=false
      this.getSize();
      this.serviceChange=true
     
    
      
     
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
    
     
    
      <div class="sr-service-card m-2 p-2"  onclick="selectService('Facade Cleaning',this)">
      <i class="far fa-circle inactive-icon"></i>
      <img src="/static/files/icons/booking/icons/FacadeCleaning.png" class="service-icon"> 
      <div class="text-center pt-2 service-title">
      Facade Cleaning
    </div></div>
   
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
      `)
      
     
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
    
     
      `)
     // selectServiceOnly('Kitchen Cleaning')
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
     
      <div class="sr-service-card m-2 p-2 service-one"  onclick="selectService('Sanitization',this)">
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
  
  responsiveClass:true,
  responsive:{
      0:{
          items:1,
          nav:true,
          loop:true
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
    bookMultipleService(){
     
      axios
        .post(
           this.url+"/customer/bookingmultiplephase2",this.serviceDetails
         
        )
        .then((response) => {
          
          console.log("booking details is "+response)
          this.phase2Result=response.data
          if(response.data.success)
          {
          
          this.getBookingDetails(response.data.booking_id)
       
      this.uploadImages()
          }
        })
         .catch((error) => {
          console.log(error);
        });
    },
    uploadImages(){
     for(var i=0;i<this.multiServiceImages.length;i++){
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
          
          console.log(response)
        
         
        })
         .catch((error) => {
          console.log(error);
        
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
    
    getMultipleSlots(){
      var gender=this.gender
      if(this.gender==" "){
        var gender=""
      }
      this.slot_loader=true
      this.onetimeslots=[]
      this.timeSlots={}
      this.time_slot[this.slotDate] = {
        selectedSlot: [],
      };
      var yr=this.oneTimeDateSelected.split('-')[0]
      var month=this.oneTimeDateSelected.split('-')[1]
      var day=this.oneTimeDateSelected.split('-')[2]
      var full_date=day+'-'+month+'-'+yr
      this.bookingonetimeslots=[]
      axios
        .post(
           this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:full_date,number_of_cleaners:this.selectedDuration.cleaners,gender:gender}
         
        )
        .then((response) => {
          this.slot_loader=true
          this.bookingonetimeslots=[]
        this.onetimeslots=[]
           this.timeSlots = response.data.slotes;
           for(var i in this.timeSlots){
            if(this.timeSlots[i].includes(2)){
              var slotNo=(parseInt(i)+2)/2
    
              this.bookingonetimeslots.push(this.slotFormat[String(slotNo)])
              this.onetimeslots.push(slotNo)
              
            }
          }
           if(response.data.Error){
             this.errMsg=response.data['Error']
             this.slot_loader=false
           }
           else{
             this.errMsg=''
             this.slot_loader=false
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
      axios
        .get(
         this.url+"/customer/ajax/getservicesizeprice?service_type=" + this.serviceType
        )
        .then((response) => {
          this.serviceSize = response.data;
          this.parseSize();
           this.facadeFilter();
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
        stain_reason: "",
        wall_type: "",
        floor_type: "",
        ceiling_type: "",
        residue: false,
        hallway_size: "",
        sides: "",
        stain_age: "",
        height:""
      };
      this.dialog = true;
      this.dialogmsg = "Add New";
      this.dialogStat = true;
      this.building = [];
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
    editItem(a, b) {
      this.dialog = true;
      this.dialogmsg = "Edit";
      this.dialogStat = false;
      (this.otherService = {
        material: a.material,
        color: a.color,
        size: a.size,
        type: a.type,
        age: a.age,
        stain: a.stain,
        stain_reason: a.stain_reason,
        wall_type: a.wall_type,
        floor_type: a.floor_type,
        ceiling_type: a.ceiling_type,
        residue: a.residue,
        hallway_size: a.hallway_size,
        sides: a.sides,
        stain_age: a.stain_age,
        section_cost:a.section_cost,
        height:a.height
  
      }),
        (this.currentItem = b);
    },
    async saveChanges() {
        await this.calcSize()
         this.otherService.section_cost=this.otherService.size.cost
      this.otherServices[this.currentItem] = this.otherService;
      this.billingData[this.currentItem].section=this.otherService
      this.dialog = false;
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
                var new_cost=left_size*max_size_val[j].unit_price
                var current_cost=max_size_val[j].cost+new_cost
                var size=this.otherService.size
                this.otherService.size={
                  name: size+' Seater',
                  cost: current_cost,
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
      this.otherService.section_cost=this.otherService.size.cost
     
      this.otherServices.push(this.otherService);
      if(this.serviceType=='Upholstery Cleaning')
      {
      this.billingData.push({
        name: this.serviceType + " - " + this.otherService.type,
        section: this.otherService,
        section_cost:this.otherService.size.cost
      });
      }
      else{
         this.billingData.push({
        name: this.serviceType ,
        section: this.otherService,
        section_cost:this.otherService.size.cost
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
        residue: false,
        hallway_size: "",
        sides: "",
        stain_age: "",
        section_cost:null
      };
      this.dialog = false;
       }
        this.findTempcost()
    },
      async addOtherServiceDialog() {
         if(this.$refs.otherServiceDialogForm.validate())
       { 
  
      await this.calcSize();
      this.otherService.section_cost=this.otherService.size.cost
     
      this.otherServices.push(this.otherService);
      if(this.serviceType=='Upholstery Cleaning')
      {
         this.billingData.push({
        name: this.serviceType + " - " + this.otherService.type,
        section: this.otherService,
      });
      }
      else{
          this.billingData.push({
        name: this.serviceType,
        section: this.otherService,
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
        residue: false,
        hallway_size: "",
        sides: "",
        stain_age: "",
        section_cost:null
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
              servcost = servcost + this.multiServicesBill[i].bill[j].section.section_cost
            }
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
                nav:true
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
        this.schedule_confirmation_dialog=false
        this.onetime_dialog=false
        this.schedule_warning=false
        if(this.scheduleStat){
            for(var i=0;i<this.multiServicesBill.length;i++){
                this.multiServicesBill[i].schedule_details={}
            }
           
        }
        this.one_time_slots[this.oneTimeDateSelected]={
            slots:[]
          }
          this.selectedDuration={
            cleaners:null,
            hours:null,
            slots:null,
            
          }
        this.onetime_dialog=true
        if(this.scheduleStat){
          this.addAllServiceTypes()
        }
        this.calcSelectedServices()
        this.newdurationcalculation();
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
  
       var sampleServicesBill={
         service:'',
         discount:false,
         bill:[],
         serviceNo:this.serviceCount,
         area_type:this.area_type,
         location_type:this.location_type,
         evaluator_note:this.evaluator_note
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
         discount:false,
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
      hallway_size: "",
      sides: "",
      stain_age: "",
      height:""
    },
        this.building=[]
        this.no_of_apartments = [];
       
        this.buildingsCompleted=false
        this.serviceData.service_details.location_type=''
         this.serviceData.service_details.area_type=''
         this.e={building:[]}
        this.no_of_building=0
        this.no_of_floors=[]
        this.calcTotal()
         this.findTotalSize()
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
        residue: false,
  
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
      for (var i = 0; i < this.no_of_building; i++) {
        this.building.push({
          floors: [],
          completed:false
        });
        this.e.building.push({
          floors: [],
          e: 1,
        });
      }
    },
    setFloors(building) {
      this.building[building - 1].floors = [];
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
        this.valid.push({
          floors:[]
        })
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
    selectDuration(duration) {
      duration.slots = duration.hours / 2;
      this.selectedDuration = duration;
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
    nextTab(build) {
      console.log("building tab is "+build)
      console.log("building tab no is "+this.no_of_building)
     this.cat_counter=this.cat_counter+1
      if (build == this.no_of_building) {
        this.buildingsCompleted = true;
       
      
      } else {
        console.log("id is " + build);
        document.querySelector("#tab" + (build + 1)).click();
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
  
            if(this.building[building].floors[floor].apartments[apartment].kitchen){
               
                for(var k=0;k<this.building[building].floors[floor].apartments[apartment].kitchens.length;k++){
                    this.building[building].floors[floor].apartments[apartment].section_cost=this.building[building].floors[floor].apartments[apartment].section_cost+this.building[building].floors[floor].apartments[apartment].kitchens[k].size.cost
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
          section: this.building[building].floors[floor].apartments[apartment],
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
    nextFloor(building, floor) {
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
  
            if(this.building[building].floors[floor - 1].kitchen){
               
                for(var k=0;k<this.building[building].floors[floor - 1].kitchens.length;k++){
                    this.building[building].floors[floor - 1].section_cost=this.building[building].floors[floor - 1].section_cost+this.building[building].floors[floor - 1].kitchens[k].size.cost
                }
            }
           // this.building[building].floors[floor - 1].section_cost=
         
           this.billSample.name= "Building " + (building + 1) + " Floor " + floor
           this.billSample.serviceNo=this.serviceCount
           Object.assign(this.billSample.section, this.building[building].floors[floor - 1]);
          
          this.billingData.push(this.billSample);
          this.billSample={
      name:'',
      section:{},
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
        this.totalCost = 0;
        
        for (var i = 0; i < this.multiServicesBill.length; i++) {
          for(var j=0;j<this.multiServicesBill[i].bill.length;j++)
          {
            if(!this.multiServicesBill[i].bill[j].section.kitchen)
            {
                          this.multiServicesBill[i].bill[j].section.section_cost=this.multiServicesBill[i].bill[j].section.size.cost
            }
        this.totalCost = this.totalCost + this.multiServicesBill[i].bill[j].section.section_cost;
          }
      }
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
   
    doSomethingAsync(k) {
      return new Promise((resolve) => {
          axios
         .get(
           this.url+"/customer/ajax/getserviceproductivity?service_type=" +
             this.schedule_serviceTypes[k]
         )
         .then((response) => {
             
              var selected_service=this.schedule_serviceTypes[k]
             console.log(response.data)
             this.durationData[this.schedule_serviceTypes[k]]=response.data
   
             /*   Calculation begins */
            console.log("selected service is"+selected_service)
         
   
             var data = response.data;
           console.log(data);
           var total_estimated_size =0
           var sofa_size=0
           var sofa_manhour=0
           var chair_manhour=0
           var sofa_productivity=0
           var chair_productivity=0
           var chair_size=0
           var new_kitchen_size=0
           var old_kitchen_size=0
           var new_kitchen_cabinet_size=0
           var old_kitchen_nocabinet_size=0
           var new_kitchen_nocabinet_size=0
           var old_kitchen_cabinet_size=0
           var new_kitchen_productivity=0
           var old_kitchen_productivity=0
           var old_kitchen_manhour=0
           var new_kitchen_manhour=0
           var highprice_facade_size=0
           var highprice_facade_manhour=0
           var lowprice_facade_size=0
           var lowprice_facade_manhour=0
           var highprice_window_size=0
           var highprice_window_manhour=0
           var lowprice_window_size=0
           var lowprice_window_manhour=0
             for(var i=0;i<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;i++)
             {
               total_estimated_size = total_estimated_size+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[i].size.max_size;
             }
            
            
             if(selected_service=='Kitchen Cleaning'){
              /* console.log("inside kitchen")
               var new_kitchen_productivity = data["newkitchen_perhour_cleaning"];
               var old_kitchen_productivity = data["oldkitchen_perhour_cleaning"];

               for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
                 
                 if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].new_kitchen){
                   console.log("inside new kitchen")
                   
                   new_kitchen_size=new_kitchen_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                                   
                 }
                 else if(!this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].new_kitchen){
                   console.log("inside old kitchen")
                  
                   old_kitchen_size= old_kitchen_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                                   
                 }

               }
               old_kitchen_manhour=old_kitchen_manhour+ parseInt( old_kitchen_size/ old_kitchen_productivity); 
               new_kitchen_manhour=new_kitchen_manhour+ parseInt(new_kitchen_size / new_kitchen_productivity);
               console.log("new kitchen prod cal"+parseInt(new_kitchen_size / new_kitchen_productivity))
               console.log("new kitchen size"+new_kitchen_size+' new kicthen prod: '+new_kitchen_productivity) 
               console.log("old kitchen"+old_kitchen_manhour+' new kicthen : '+new_kitchen_manhour)
               var manhour= old_kitchen_manhour+new_kitchen_manhour
               console.log("kicthen amhr is"+manhour)
               //Addons Manhour
               for(var add=0;add<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;add++){
                 var addons_available=this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[add].addonsections
                 var addons_manhour=0
                 for(var addon=0;addon<addons_available.length;addon++){
                    addons_manhour=addons_manhour+parseInt(this.getProductivityAddonByName(addons_available[addon]))*addons_available[addon].quantity
                 }
              }
              console.log("addons manhour is "+addons_manhour)
              manhour=manhour+addons_manhour*/
              for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
                 
                if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].new_kitchen){
                 if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].is_cabinet)
                  {
                    new_kitchen_cabinet_size=new_kitchen_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                  }
                  else{
                    new_kitchen_nocabinet_size=new_kitchen_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size) 
                  }               
                }
                else if(!this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].new_kitchen){
                  console.log("inside old kitchen")
                  if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].is_cabinet)
                  {
                 
                  old_kitchen_cabinet_size= old_kitchen_cabinet_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                  }
                  else{
                    old_kitchen_nocabinet_size= old_kitchen_nocabinet_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size) 
                  }
                                  
                }

              }
          var manhour =
          parseInt(
            new_kitchen_cabinet_size / data["newkitchenwithcabinet_perhour_cleaning"]
          ) +
          parseInt(
            new_kitchen_nocabinet_size / data["newkitchenwithout_perhour_cleaning"]
          )+
          parseInt(
            old_kitchen_cabinet_size / data["oldkitchenwithcabinet_perhour_cleaning"]
          )+
          parseInt(
            old_kitchen_nocabinet_size / data["oldkitchenwithoutcabinet_perhour_cleaning"]
          )
          //To find addons man hour 
          var addon_manhour=0
          for(var ao=0;ao<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;ao++){
              for(var addon=0;addon<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].addonsections.length;addon++){
                if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].addonsections[addon].selected){
                  if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].addonsections[addon].details.category){
                    addon_manhour=addon_manhour+(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].addonsections[addon].quantity*(parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].addonsections[addon].selected_size.max_size)/this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].section.addonsections[addon].details.productivity))
                  }
                  else{
                  addon_manhour=addon_manhour+this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].addonsections[addon].details.productivity*this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[ao].addonsections[addon].quantity
                  }
                }
              }
          
          }
          console.log("addon manhour is"+addon_manhour)
          manhour=parseInt(manhour)+parseInt(addon_manhour)

               
             }
             else if(selected_service=='Upholstery Cleaning'){
                sofa_productivity = data["chair_perhour_cleaning"];
                chair_productivity = data["sofa_perhour_cleaning"];
             for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
               
               if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].upholstery_type=='CHAIR'){
               
               
                 chair_size=chair_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                                 
               }
               else  if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].upholstery_type=='SOFA'){
                if(!isNaN(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size)){
                  sofa_size=sofa_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size)  
                }
                else{
                  sofa_size=sofa_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)  
                }
                 
                 
                                 
               }

             }
             sofa_manhour=sofa_manhour+ parseInt(sofa_size / sofa_productivity); 
             chair_manhour=chair_manhour+ parseInt(chair_size / chair_productivity); 
             var manhour=chair_manhour+sofa_manhour
           }
             else if(selected_service=='Facade Cleaning'){
                 var highprice_facade_productivity = data["highpricefacade_perhour_cleaning"];
                 var lowprice_facade_productivity = data["lowpricefacade_perhour_cleaning"];
               for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
                 
                 if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].is_highprice_facade){
                 
                 
                   highprice_facade_size=highprice_facade_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                                   
                 }
                 else  if(!this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].is_highprice_facade){
                  
                   
                   lowprice_facade_size=lowprice_facade_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                                   
                 }

               }
               highprice_facade_manhour=highprice_facade_manhour+ parseInt(highprice_facade_size / highprice_facade_productivity); 
               lowprice_facade_manhour=lowprice_facade_manhour+ parseInt(lowprice_facade_size / lowprice_facade_productivity); 
               var manhour=highprice_facade_manhour+lowprice_facade_manhour
             }
             else if(selected_service=='Window Cleaning'){
               var highprice_window_productivity = data["highpricewindow_perhour_cleaning"];
               var lowprice_window_productivity = data["lowpricewindow_perhour_cleaning"];
             for(var b=0;b<this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill.length;b++){
               
               if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].is_highprice_window){
               
               
                 highprice_window_size=highprice_window_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                                 
               }
               else  if(!this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].is_highprice_window){
                
                 
                 lowprice_window_size=lowprice_window_size+parseInt(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].bill[b].size.max_size)   
                                 
               }

             }
             highprice_window_manhour=highprice_window_manhour+ parseInt(highprice_window_size / highprice_window_productivity); 
             lowprice_window_manhour=lowprice_window_manhour+ parseInt(lowprice_window_size / lowprice_window_productivity); 
             var manhour=highprice_window_manhour+lowprice_window_manhour
           }
            /* else if(selected_service=='Upholstry Cleaning'){
               if(this.multiServicesBill[this.schedule_serviceTypes_selected[k]].new_kitchen){
                 var productivity = data["newkitchen_perhour_cleaning"];
               }
               else{
                 var productivity = data["oldkitchen_perhour_cleaning"];
               }
               
             }*/
             else{
               var productivity = data["perhour_cleaning"];
               console.log("productivity is "+productivity)
               console.log("total size is "+total_estimated_size)
               var manhour = parseInt(total_estimated_size / productivity);
               if(manhour<1){
                manhour=1
              }
             }
           
            
           
        
           //optimal finding
           this.totalmanhour=this.totalmanhour+manhour
           console.log("total man hour is "+this.totalmanhour)
           var r = 2 ** (this.totalmanhour.toString().length - 1);
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
      this.duration_loader=true
      this.totalmanhour=0
       this.duration=[]
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
              Math.round(manhour / (middle_hours + 2)) <= max_cleaners
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
          this.duration_loader=false
  })
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
    /* header methods begins */
    selectTab(service){
      this.selectedTab=service
    },
    goTo(url){
      window.location.href=url
    },
    changeToArabic(){
      var servicePage=false
      var uri = window.location.href.split('?lang');
       var uri2=window.location.href.split('&lang') 
       if(uri2.length>1){
          uri=uri2
          servicePage=true
       } 
      this.lang="ar"
      if(uri){
      if(uri.length<2 && uri2.length<2){
          if(!servicePage){
              window.location.href=window.location.href+'?lang=ar'
          }
          else{
              window.location.href=window.location.href+'&lang=ar'
          }
          
      }
      else{
          if(uri[1]=='=ar')
          {
          window.location.href=window.location.href
          }
          else{
              if(!servicePage){
              window.location.href=uri[0]+'?lang=ar'
              }
              else{
                  window.location.href=uri[0]+'&lang=ar'
              }
          }
      }
  }
  },
  changeToEnglish(){
      var servicePage=false
      var uri = window.location.href.split('?lang');
       var uri2=window.location.href.split('&lang') 
       if(uri2.length>1){
          uri=uri2
          servicePage=true
       } 
       if(uri){
          this.lang='en'
          if(uri.length<2 && uri2.length<2 ){
              if(!servicePage){
              window.location.href=window.location.href+'?lang=en'
              }
              else{
                  window.location.href=window.location.href+'&lang=en'
              }
          }
          else{
              if(uri[1]=='=en')
              {
              window.location.href=window.location.href
              }
              else{
                  if(!servicePage){
                  window.location.href=uri[0]+'?lang=en'
                  }
                  else{
                      window.location.href=uri[0]+'&lang=en'
                  }
              }
          }
      }
  },
changeLang(){
   var servicePage=false
  var uri = window.location.href.split('?lang');
   var uri2=window.location.href.split('&lang') 
   if(uri2.length>1){
      uri=uri2
      servicePage=true
   } 
  if(this.arabic){
      
      this.lang="ar"
      if(uri){
      if(uri.length<2 && uri2.length<2){
          if(!servicePage){
              window.location.href=window.location.href+'?lang=ar'
          }
          else{
              window.location.href=window.location.href+'&lang=ar'
          }
          
      }
      else{
          if(uri[1]=='=ar')
          {
          window.location.href=window.location.href
          }
          else{
              if(!servicePage){
              window.location.href=uri[0]+'?lang=ar'
              }
              else{
                  window.location.href=uri[0]+'&lang=ar'
              }
          }
      }
  }
     
  }
  else{
      if(uri){
      this.lang='en'
      if(uri.length<2 && uri2.length<2 ){
          if(!servicePage){
          window.location.href=window.location.href+'?lang=en'
          }
          else{
              window.location.href=window.location.href+'&lang=en'
          }
      }
      else{
          if(uri[1]=='=en')
          {
          window.location.href=window.location.href
          }
          else{
              if(!servicePage){
              window.location.href=uri[0]+'?lang=en'
              }
              else{
                  window.location.href=uri[0]+'&lang=en'
              }
          }
      }
  }
}
 

},     
selectNav(nav){
this.activeWebTab = true;  
this.activeItem=nav 
this.category='Detailed Cleaning'
this.serviceType='General Cleaning'
},
selectWebCategory(category){
this.activeWebTab = true;  
this.category=category;
if(this.category=='Detailed Cleaning'){
    this.serviceType='General Cleaning'
}
if(this.category=='Special Care'){
  this.serviceType='Upholstery Cleaning'
}
if(this.category=='Kitchen Cleaning'){
  this.serviceType='Kitchen Cleaning'
}
if(this.category=='Infection Control'){
  this.serviceType='Sanitization & Disinfection'
}
},
selectService(service){
this.activeWebTab = true;  
this.serviceType=service
 
},
mouseleave(){
this.activeWebTab = false; 
},
selectBooking(type){
console.log("i run")
this.selectedBooking=type
},
goToBooking(service){
var url='http://testbook.bleach-kw.com/#/'
window.location.href=url+"?service="+service
},
goToBookingPage(){
var url='http://testbook.bleach-kw.com/#/'
if(this.selectedBooking=='Evaluation')
{
window.location.href=url+'evaluator'
}
else{
  window.location.href=url
}
},
slideChange(a){

if(this.activeService=='Detailed Cleaning' && a==3){
    this.activeService='Special Care'
}
else if(this.activeService=='Special Care' && a==4){
  this.activeService='Kitchen Cleaning'
}
else if(this.activeService=='Kitchen Cleaning' && a==5){
  this.activeService='Infection Control'
}
else if(a==4 && this.activeService=='Infection Control'){
  this.activeService='Kitchen Cleaning'
}
else if(a==2 && this.activeService=='Infection Control'){
  this.activeService='Detailed Cleaning'
}
else if(a==3 && this.activeService=='Kitchen Cleaning'){
  this.activeService='Special Care'
}
else if(a==2 && this.activeService=='Special Care'){
  this.activeService='Detailed Cleaning'
}
else if(a==1 && this.activeService=='Detailed Cleaning'){
  this.activeService='Infection Control'
}
console.log("active service is"+this.activeService +"a:"+a)
},
prevService(){

},
getBookedServices(){
  this.multiServicesBill=[]
  axios.get(this.url+'/customer/evaluatorbookingmultiplephase3/customer/'+this.custId).then(response=>{

    this.bookedServiceDetails=response.data.evaluation_details
    this.payment_total_cost=this.bookedServiceDetails[0].evaluation.total_cost
    this.payment_status=response.data.order_details.payment_status
    this.booking_status=response.data.booking_status
    this.order_no=response.data.order_details.order_no
    this.getBookingTime(response.data.order_details.order_no)
    if(this.booking_status){
      this.amount_discount=response.data.discount_details.discount
      this.amount_payable=response.data.discount_details.total_cost
      this.payable_amount=this.amount_payable
      this.amount_subtotal=response.data.discount_details.estimated_cost
      this.evaluation_id=response.data.secret_code
    }

    if(this.bookedServiceDetails.length>0){
      this.multiAddress=true
    }
    this.selectedAddress=this.bookedServiceDetails[0]
    var currentAddress=this.bookedServiceDetails[0]
   
      this.currentAddressIndex=0
   
    var serviceBookedDetails=currentAddress.evaluation_book_evaluation_details
    for(var i=0;i<serviceBookedDetails.length;i++)
    {
      var scheduleDetails={
        id:serviceBookedDetails[i].id ,
        evaluation_details_id:this.selectedAddress.id,
        area_type:serviceBookedDetails[i].area_type,
        bill:[],
        evaluator_note:serviceBookedDetails[i].evaluator_note,
        location_type:serviceBookedDetails[i].location_type,
        schedule_details:{},
        service:serviceBookedDetails[i].service_type.name,
        total_cost:serviceBookedDetails[i].total_cost,
        discount:false
      }
      for(var j=0;j<serviceBookedDetails[i].evaluationsection_book.length;j++) {
        scheduleDetails.bill.push(serviceBookedDetails[i].evaluationsection_book[j])
      }
      this.multiServicesBill.push(scheduleDetails)
    }
    this.gotData=true
    this.rearrangeSize()
  }).catch(e=>{
    console.log(e)
  })
},
async rearrangeSize(){
 
  for(var i=0;i<this.multiServicesBill.length;i++){
   
    var productivity= await this.getTheProd(this.multiServicesBill[i].service)
   
    for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
      /* If old bookings */
      if(!isNaN(this.multiServicesBill[i].bill[j].size)){
      
        for(var p in productivity){
           /** for kitchen Cleaning*/
           if(this.multiServicesBill[i].service=='Kitchen Cleaning'){
              if(multiServicesBill[i].bill[j].new_kitchen){
                if(productivity[p].name==this.multiServicesBill[i].bill[j].size && productivity[p].is_newkitchen && parseInt(this.multiServicesBill[i].bill[j].size)>=productivity[p].min_size && parseInt(this.multiServicesBill[i].bill[j].size)<=productivity[p].max_size){
                  this.multiServicesBill[i].bill[j].size=productivity[p]
                }
              }
           }
           
        
      /**  for general,deep,carparking,sterilization....... */
      else{

      
          if((parseInt(this.multiServicesBill[i].bill[j].size)>=productivity[p].min_size) && (parseInt(this.multiServicesBill[i].bill[j].size)<=productivity[p].max_size)){
            
            this.multiServicesBill[i].bill[j].size=productivity[p]
           
          }
         
      }
        
        }
      }

      /* new bookings */
      else{
        console.log("just called me"+ "i am "+this.multiServicesBill[i].service)
        console.log("i m inside new booking")
      if(this.multiServicesBill[i].service=='Kitchen Cleaning'){
        
        if(this.multiServicesBill[i].bill[j].new_kitchen)
        {
          for(var p in productivity){
        if(productivity[p].name==this.multiServicesBill[i].bill[j].size && productivity[p].is_newkitchen){
          this.multiServicesBill[i].bill[j].size=productivity[p]
        }
      }
      }
      else {
        for(var p in productivity){
        if(productivity[p].name==this.multiServicesBill[i].bill[j].size && !productivity[p].is_newkitchen){
          this.multiServicesBill[i].bill[j].size=productivity[p]
        }
      }
      }
      }
      else if(this.multiServicesBill[i].service=='Upholstery Cleaning'){
        console.log("i m inside upholsetry")
        console.log("up type is "+this.multiServicesBill[i].bill[j].upholstery_type)
        var type=""
         for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
           if(this.multiServicesBill[i].bill[j].upholstery_type=='SOFA'){
             type="SOFA"
             if(this.multiServicesBill[i].bill[j].size.includes('Seater')){
              this.multiServicesBill[i].bill[j].size=this.multiServicesBill[i].bill[j].size.split(" ")[0]
              console.log("section size is "+this.multiServicesBill[i].bill[j].size.split(" ")[0])
               this.multiServicesBill[i].bill[j].upholstery_type="SOFA"
              
             }
             else{
              for(var p in productivity){
        
      
                if(productivity[p].name==this.multiServicesBill[i].bill[j].size && productivity[p].upholstery_type=='SOFA'){
                  this.multiServicesBill[i].bill[j].size=productivity[p]
                }
              
              
            }
             }
             //this.sections[j].size=this.this.sections[j].size.split(" ")[0]
             
           }
           else if(this.multiServicesBill[i].bill[j].upholstery_type=='CHAIR'){
             type="CHAIR"
             this.multiServicesBill[i].bill[j].upholstery_type="CHAIR"
             for(var p in productivity){
        
      
              if(productivity[p].name==this.multiServicesBill[i].bill[j].size && productivity[p].upholstery_type=='CHAIR'){
                this.multiServicesBill[i].bill[j].size=productivity[p]
              }
            
            
          }
           }
           console.log("type is"+type)
           
          
         }
           
       }
       else if(this.multiServicesBill[i].service=='Facade Cleaning'){
        for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
        for(var p in productivity){
        if(this.multiServicesBill[i].bill[j].is_highprice_facade){
          if(productivity[p].name==this.multiServicesBill[i].bill[j].size && productivity[p].is_highprice_facade ){
            this.multiServicesBill[i].bill[j].size=productivity[p]
          }
          
        }
        else{
          if(productivity[p].name==this.multiServicesBill[i].bill[j].size && !productivity[p].is_highprice_facade){
            this.multiServicesBill[i].bill[j].size=productivity[p]
          }
        }
      
          
        
        
      }
    }
       }
       else if(this.multiServicesBill[i].service=='Window Cleaning'){
        for(var j=0;j<this.multiServicesBill[i].bill.length;j++){
        for(var p in productivity){
        if(this.multiServicesBill[i].bill[j].is_highprice_window){
          if(productivity[p].name==this.multiServicesBill[i].bill[j].size && productivity[p].is_highprice_window ){
            this.multiServicesBill[i].bill[j].size=productivity[p]
          }
          
        }
        else{
          if(productivity[p].name==this.multiServicesBill[i].bill[j].size && !productivity[p].is_highprice_window){
            this.multiServicesBill[i].bill[j].size=productivity[p]
          }
        }
      
          
      }
        
      }
       }  
      else{
        console.log("i m inside general")
      for(var p in productivity){
        
      
          if(productivity[p].name==this.multiServicesBill[i].bill[j].size){
            this.multiServicesBill[i].bill[j].size=productivity[p]
          }
        
        
      }
    }
  }
    }
  }
  
           
  
},
async getTheProd(service){
  var res={}
  await axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+service).then( response =>{
  
    res= response.data
  })
  return res
  

  
},
reCalcAddressData(){
  console.log("called me")
  this.multiServicesBill=[]
  currentAddress=''
  for(var j=0;j<this.bookedServiceDetails.length;j++){
    if(this.bookedServiceDetails[j].id==this.selectedAddress.id){
      currentAddress=this.bookedServiceDetails[j]
      break
    }
  }
  console.log("booked service is"+JSON.stringify(currentAddress))
//  console.log("booked service is"+JSON.stringify(this.bookedServiceDetails[this.selectedAddress]))

  var serviceBookedDetails=currentAddress.evaluation_book_evaluation_details
  for(var i=0;i<serviceBookedDetails.length;i++)
  {
    var scheduleDetails={
      id:serviceBookedDetails[i].id,
      evaluation_details_id:this.bookedServiceDetails[this.currentAddressIndex].id,
      area_type:serviceBookedDetails[i].area_type,
      bill:[],
      evaluator_note:serviceBookedDetails[i].evaluator_note,
      location_type:serviceBookedDetails[i].location_type,
      schedule_details:{},
      service:serviceBookedDetails[i].service_type.name,
      total_cost:serviceBookedDetails[i].total_cost
    }
    for(var j=0;j<serviceBookedDetails[i].evaluationsection_book.length;j++) {
      scheduleDetails.bill.push(serviceBookedDetails[i].evaluationsection_book[j])
    }
    this.multiServicesBill.push(scheduleDetails)
  }
  this.gotData=true
  this.rearrangeSize()

},
getSettings(){
  axios.get(this.url+'/api/discount-settings/').then(response=>{
    this.settings=response.data.discount_details
  })
},
bookLetCustService(){
  var gender=this.gender
  var discount=this.calculateDiscount()
  this.payable_amount=this.payment_total_cost-discount
  if(this.gender==" "){
    gender=""
  }
  if(this.currentAddressIndex==0){
    this.custServiceScheduled={
      "booking_type":"",
      "service_details":{},
      "discount":discount,
      "gender":gender
    },
    this.custServiceScheduled.booking_type='together'
  }
  for(var i=0;i<this.multiServicesBill.length;i++){
    this.custServiceScheduled.service_details[i+1]={
      "id":this.multiServicesBill[i].id,
      "evaluation_details_id":this.multiServicesBill[i].evaluation_details_id,
      "schedule_details":this.multiServicesBill[i].schedule_details
    }
  }
  this.completedAddress.push(this.currentAddressIndex)
  this.currentAddressIndex=this.currentAddressIndex+1
  
  this.selectedAddress=this.bookedServiceDetails[this.currentAddressIndex]
  //this.payment_status=this.bookedServiceDetails[this.currentAddressIndex].order_details.payment_status
 // this.payment_total_cost=this.bookedServiceDetails[this.currentAddressIndex].evaluation.total_cost
 console.log("service details length is"+this.bookedServiceDetails.length+"address index is"+this.currentAddressIndex)

    
  
  this.sendLetCustScheduled()
  if(this.currentAddressIndex!=this.bookedServiceDetails.length){
    this.reCalcAddressData()
  }
  
  
},
sendLetCustScheduled(){
  var gender=this.gender
  this.btnLoader=true
  var discount=this.calculateDiscount()
  this.payable_amount=this.payment_total_cost-discount
  if(this.gender==" "){
    gender=""
  }
  if(!this.scheduleStat){
    var ch_count=0
    for(var ch in this.scheduleGroup){
      if(this.scheduleGroup[ch].length>0){
        var serviceDetails={
          "booking_type":"together",
          "service_details":{},
          "gender":gender,
          "discount":discount
        }
        for(var j=0;j<this.scheduleGroup[ch].length;j++){
          var service=this.scheduleGroup[ch]
          serviceDetails.service_details[j+1]={
            "id":this.multiServicesBill[service[j]].id,
            "evaluation_details_id":this.multiServicesBill[service[j]].evaluation_details_id,
            "schedule_details":this.multiServicesBill[service[j]].schedule_details,
            
          }
        }
        axios.post(this.url+'/customer/evaluatorbookingmultiplephase3/customer/'+this.custId,serviceDetails).then(response=>{
          this.evaluation_id=response.data.secret_code
          this.eval_details=response.data
          this.btnLoader=false
          ch_count=ch_count+1
          if(ch_count==(Object.keys(this.scheduleGroup).length) && this.currentAddressIndex==this.bookedServiceDetails.length){
            if(this.eval_details.payment_status=='PENDING'){
              this.counterTime='5:00'
              startTimer()
              this.goToPaymentDialog()
            }
            else{
           //   this.success_booking_dialog=true
            }
           
            
          }
          
        
        })
      }
     
      
    }
   

  }
  else{
    axios.post(this.url+'/customer/evaluatorbookingmultiplephase3/customer/'+this.custId,this.custServiceScheduled).then(response=>{
      this.evaluation_id=response.data.secret_code
      this.eval_details=response.data
      this.btnLoader=false
      if(this.currentAddressIndex==this.bookedServiceDetails.length){
        if(this.eval_details.payment_status=='PENDING'){
          this.counterTime='5:00'
          startTimer()
          this.goToPaymentDialog()
         
        }
        else{
         // this.success_booking_dialog=true
        }
      }
     
    })
  }
  
 
},
getBookingTime(orderno){
  axios.get(this.url+'/api/booking-expiry-check/?order_no='+orderno).then(response=>{
    this.booking_time=response.data.created
    console.log("inside time")
    if(this.booking_status)
    {
      var currentTime = moment().utcOffset("+03:00").format('DD-MM-YYYY hh:mm:ss A')
     
     console.log("current time is"+currentTime+"booking time is"+this.booking_time)

      var startTime = moment(this.booking_time, "DD-MM-YYYY hh:mm:ss A").format("DD-MM-YYYY hh:mm:ss A");
      var endTime =moment(currentTime,'DD-MM-YYYY hh:mm:ss A').locale('ar-kw').format("DD-MM-YYYY hh:mm:ss A")
     
      
      console.log("start is"+startTime+"end is"+endTime)
      // calculate total duration
      
      var duration = moment.duration(moment(endTime,'DD-MM-YYYY hh:mm:ss A').diff(moment(startTime,'DD-MM-YYYY hh:mm:ss A')));

      // duration in hours
      var hours = parseInt(duration.asHours());
      var seconds=(300-parseInt(duration.asSeconds()))%60;
      
      // duration in minutes
      var minutes = parseInt(duration.asMinutes());
      console.log( minutes+' minutes.  seconds'+seconds);
       if(minutes>5){
        this.cancelBooking(orderno)
      //  console.log("called cancel booking")
       }  
        this.counterTime=(5-minutes)+':'+seconds
        startTimer()
      
    }

  })
},
cancelBooking(orderno){
  axios.post(this.url+'/api/booking-expiry/',{order_no:orderno}).then(response=>{
    setTimeout(function(){ location.reload(); }, 5000);
    
  })

},
async getAddons(){
  this.addons=[]
  var ser = 'Kitchen Cleaning'
  axios.get(this.url+'/customer/ajax/getserviceaddons?service_type='+ser).then(response=>{
    this.addons=response.data.service_addons
   
   
  }).catch((error)=>{
    console.log(error)
  })
},
getProductivityAddonByName(addon){
var name=addon.name
if(addon.other_details){
  var size=JSON.stringify(addon.other_details)
}

  for(var i=0;i<this.addons.length;i++){
    if(this.addons[i].name==name){
      if(this.addons[i].category){
        if(this.addons[i].category==size){
          return this.addons[i].productivity
        }
      }
      else{
        return this.addons[i].productivity
      }
    }
  }
}
    
  },

  mounted() {
    
    this.url = api;
    const urlSearchParams = new URLSearchParams(window.location.search);
    const params = Object.fromEntries(urlSearchParams.entries());
    this.custId=params.id
    this.getBookedServices()
   // this.getServices()
   // this.getAreaTypes()
   this.getSettings()
    this.getIp()
    //this.getGovernorate()
    //this.dummyDataGenerator(3)
    console.log("current time is" + moment().format());
  
    this.dateSelected = moment().format().split("T")[0];
    this.today = moment().format().split("T")[0];
    this.oneTimeDateSelected=moment().format().split("T")[0];
    this.one_time_slots[this.oneTimeDateSelected]={
      slots:[]
    }
    this.formatDate();
       // this.getMultipleSlots()
       
     //   this.changeNewKitchen()
  
    this.selectCategory('Detailed Cleaning')
    
    //moment.tz.setDefault("Asia/Baghdad");
    
       
        
  },
  created()
  {
    
  },
      
     
     
    });
    function startTimer() {
 
      var presentTime = app.counterTime;
      
      
      var timeArray = presentTime.split(/[:]+/);
      var m = timeArray[0];
      var s = checkSecond((timeArray[1] - 1));
      if(s==59){m=m-1}
      if(m<0){
        return
      }
      if(m==0 &&s=='05'){
        app.cancelBooking(this.order_no)
      }
      app.counterTime =
        m + ":" + s;
      
      setTimeout(startTimer, 1000);
      
    }
    
    
  
  
  
  
  