
      $(document).ready(function(){
   
new Vue({
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
    data: {
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
    valid:true,
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
    url:'https://test.bleach-kw.com',
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
  activeTab: "Services",
  selectedService: {
      name:'General Cleaning'
  },
  serviceSize: {},

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
  ip_address:''

       
      },
      methods: {
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
      
        if(this.$refs.kitchenForm[0].validate())
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
      
        if(this.$refs.kitchenDialogForm.validate())
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
  },
  selectCategory(item){
    this.ser_counter++
    this.refresh++
    this.currentServices=[]
this.detailedCleaningServices=[]
this.specialCareServices=[]
this.kitchenCleaningServices=[]
this.infectionControlServices=[]
    this.selectedCategory=item
    if(item=='Detailed Cleaning'){
       for(var i=0;i<this.services.length;i++){
         if(this.services[i].name=='General Cleaning'||this.services[i].name=='Deep Cleaning'||this.services[i].name=='Facade Cleaning'||this.services[i].name=='Car Parking Umbrella'||this.services[i].name=='Window Cleaning'||this.services[i].name=='Outdoor Cleaning'||this.services[i].name=='Storage Area'){
             this.detailedCleaningServices.push(this.services[i])
               this.currentServices.push(this.services[i])
               this.selectedService={name:'General Cleaning'}
               this.serviceType='General Cleaning'

         }
    
    }
    }
    else{
       if(item=='Special Care'){
       for(var i=0;i<this.services.length;i++){
         if(this.services[i].name=='Upholstery Cleaning'||this.services[i].name=='Carpet Cleaning'||this.services[i].name=='Mattress Cleaning'){
             this.specialCareServices.push(this.services[i])
              this.currentServices.push(this.services[i])
               this.selectedService={name:'Upholstery Cleaning'}
                this.serviceType='Upholstery Cleaning'
         }
    
    }
    }
     else{
        if(item=='Kitchen Cleaning'){
      for(var i=0;i<this.services.length;i++){
         if(this.services[i].name=='Kitchen Cleaning'){
             this.kitchenCleaningServices.push(this.services[i])
              this.currentServices.push(this.services[i])
               this.selectedService={name:'Kitchen Cleaning'}
                this.serviceType='Kitchen Cleaning'
         }
    
    }
        }
        else{
           if(item=='Infection Control'){
               for(var i=0;i<this.services.length;i++){
         if(this.services[i].name=='Sterilization'){
             this.infectionControlServices.push(this.services[i])
              this.currentServices.push(this.services[i])
               this.selectedService={name:'Sterilization'}
                this.serviceType='Sterilization'
         }
    
    }
           }
        }
    }
   
    }
 this.getSize();
 

   
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
    axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.serviceTypes,cleaning_date:this.slotDate,number_of_cleaners:this.selectedDuration.cleaners}
       
      )
      .then((response) => {
         this.timeSlots = response.data.slotes;
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
  useWebWorker: true
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
  goToService(){
    this.activeTab='Service'
    reinit()
  },
  goToSchedule(){
      this.activeTab='Schedule'
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
 /*  destroyCarousel()*/
     var sampleServicesBill={
       service:'',
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
        completed: false,
        paint_residue: false,
        upholsteries: ["Sofa", ""],
      });
      this.e.building[building - 1].floors.push({
        floors: [],
        e: 1,
      });
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
        kitchen: false,
        kitchens: [],
        keynotes: {},
      });
    }
  },
  selectDuration(duration) {
    duration.slots = duration.hours / 3;
    this.selectedDuration = duration;
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
     
  },
  findTempcost(){
    this.tempCost=0
    for(var i=0;i<this.billingData.length;i++){
        this.tempCost=this.tempCost+this.billingData[i].section.section_cost
    }
  },
  nextFloor(building, floor) {
      console.log('validate is '+this.$refs.form)
     if(this.$refs.form[0].validate())
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
          this.serviceTypes[k]
      )
      .then((response) => {
          
           var selected_service=this.serviceTypes[k]
          console.log(response.data)
          this.durationData[this.serviceTypes[k]]=response.data

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
          var total_newkitchen_size = this.new_kitchen_size;
          var total_oldkitchen_size = this.old_kitchen_size;
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
          console.log("productivity is "+productivity)
          var manhour = parseInt(total_estimated_size / productivity);
        }
        console.log("size estimated is" + total_estimated_size);
         console.log("sofa size estimated is" + total_sofa_size);
           console.log("chair size estimated is" + total_chair_size)
           console.log("manhour  estimated is" + manhour);
        //optimal finding
        this.totalmanhour=this.totalmanhour+manhour
        console.log("total man hour is "+this.totalmanhour)
        var r = 2 ** (this.totalmanhour.toString().length - 1);
        var mod = this.totalmanhour % r;

        if (mod > parseInt(r / 2)) {
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
  let promises = [];
  var count=0;
     for(var k=0;k<this.serviceTypes.length;k++){
      
     
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
        var convertion_r = 3;
        var convertion_mod = pair[1] % convertion_r;
        var highest_cleaner=Math.max(...this.maxCleaners)
        var lowest_cleaner=Math.min(...this.maxCleaners)

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
            Math.round(manhour / (middle_hours - 3)) > 0 &&
            Math.round(manhour / (middle_hours - 3)) <= lowest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours - 3)),
              middle_hours - 3,
            ]);
            lower_loop = 1;
          }
          if (
            Math.round(manhour / (middle_hours + 3)) > 0 &&
            Math.round(manhour / (middle_hours + 3)) <= lowest_cleaner
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
            Math.round(manhour / (middle_hours - 6)) <= lowest_cleaner &&
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
            Math.round(manhour / (middle_hours + 6)) <= lowest_cleaner &&
            lower_loop == 0
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 6)),
              middle_hours + 6,
            ]);
            upper_loop = 1;
          }
        } else if (middle_element == 0 && lowest_cleaner > 0) {
          //1st
          duration_list.push([1, middle_hours]);

          //2nd
          if (
            Math.round(manhour / (middle_hours + 3)) > 0 &&
            Math.round(manhour / (middle_hours + 3)) <= lowest_cleaner
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
            Math.round(manhour / (middle_hours + 6)) <= lowest_cleaner
          ) {
            duration_list.push([
              Math.round(manhour / (middle_hours + 6)),
              middle_hours + 6,
            ]);
          } else {
            duration_list.push([1, middle_hours + 6]);
          }
        } else {
          middle_element = lowest_cleaner;
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
            Math.round(manhour / (middle_hours + 3)) <= lowest_cleaner
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
   
  this.getServices()
  this.getAreaTypes()
  this.getIp()
  this.getGovernorate()
  this.selectCategory('Detailed Cleaning')
  
  moment.tz.setDefault("Asia/Baghdad");
  console.log("current time is" + moment().format());

  this.dateSelected = moment().format().split("T")[0];
  this.today = moment().format().split("T")[0];
  this.formatDate();
     // this.getMultipleSlots()
     
      this.changeNewKitchen()
     
      
},
created()
{
  
},
    
   
   
  });
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
            items:4,
            nav:true,
            loop:false
        }
    }
});
$('#service-carousel').owlCarousel({
    loop:false,
    
    responsiveClass:true,
    responsive:{
        0:{
            items:4,
            nav:true
        },
        600:{
            items:4,
            nav:false
        },
        1000:{
            items:4,
            nav:true,
            loop:false
        }
    }
});



});

function refreshService() {
    console.log("service refreshed")
    var $owl=$('#service-carousel').owlCarousel({
        loop:false,
        
        responsiveClass:true,
        responsive:{
            0:{
                items:4,
                nav:true
            },
            600:{
                items:4,
                nav:false
            },
            1000:{
                items:4,
                nav:true,
                loop:false
            }
        }
    });
    
}
function destroyCarousel(){
  
   


/*$('#category-carousel').owlCarousel('destroy');
$('#category-carousel').owlCarousel({touchDrag: false, mouseDrag: false});

$('#service-carousel').owlCarousel('destroy');
$('#service-carousel').owlCarousel({touchDrag: false, mouseDrag: false});*/
/*$('#service-carousel').data('owl.carousel').destroy();  
$('#service-carousel').owlCarousel({touchDrag: false, mouseDrag: false});
/*$('#category-carousel').data('owlCarousel').reinit();*/
    $('#category-carousel').trigger('destroy.owl.carousel').removeClass('owl-carousel owl-loaded');
    $('#category-carousel').find('.owl-stage-outer').children().unwrap();
    $('#service-carousel').trigger('destroy.owl.carousel').removeClass('owl-carousel owl-loaded');
    $('#service-carousel').find('.owl-stage-outer').children().unwrap();
}
function reinit(){
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
                items:4,
                nav:true,
                loop:false
            }
        }
    });
    $('#service-carousel').owlCarousel({
        loop:false,
        
        responsiveClass:true,
        responsive:{
            0:{
                items:4,
                nav:true
            },
            600:{
                items:4,
                nav:false
            },
            1000:{
                items:4,
                nav:true,
                loop:false
            }
        }
    });
    console.log("carousel reinitialized")
}
    