

var app = new Vue({
  el: '#app',
  delimiters: ["<%","%>"],
  vuetify: new Vuetify({
      theme: {
          themes: {
            light: {
              primary: '#348695', 
              secondary: '#348695', 
              accent: '#348695', 
            },
          },
        },
     
  }),
  data () {
  return {
    buildingsCompleted:false,
    date: null,
      menu: false,
    ImageDetails:{
      url:'',
      file:''
    },
    dateSelected:'',
    userStat:true,
    images: [],
    duration:[],
    totalCost:0,
    billingData:[],
    dialogStat:'',
      sizeData:[],
      currentItem:'',
  service:'test',
  dialog:false,
  dialogmsg:'',
  otherServices:[],
  otherService:{
    material:'',
    
    color:'',
    size:'',
    type:'',
    age:'',
    stain:false,
    stain_reason:'',
    wall_type:'',
    floor_type:'',
    ceiling_type:'',
    residue:false,
    hallway_size:'',
    sides:'',
    stain_age:''
  },
  color:['Blue','Yellow','Orange','Red','Black','White'],
  material:['Material 1','Material 2','Material 3','Material 4'],
  upholsteryType:['Sofa','Chair','Curtain'],
  upholsterySize1:['Small','Medium','Large','Xtra Large'],
  upholsterySize2:['Small','Medium','Large'],
  upholsterySize3:['Small','Medium','Large'],
  tab:'tab1',
  e6: 1,
  e1:1,
    serviceType:'',
    apartment:[],
    no_of_apartments:[],
    serviceSize:{},
    e:{
      building:[]
    },
    no_of_building:0,
    building:[],
    no_of_floors:[],
    buildings:['1','2','3','4','5','6','7','8','9','10'],
    serviceSection:{
        service_type:'',
        area_type:'',
        location_type:'',
        sections:{

        }
    },
    area_types:['APARTMENT','HOUSE','VILLA','OFFICE','GYM','RESTAURANT','COFFEE SHOP','MALL','CINEMA'],
    location_types:['Post Construction','Post Renovation','Fully Furnished','Empty Area'],
    splitData:['8'],
    selectTest:'',
    selectedDuration:'8',
    size:['SMALL','MEDIUM','LARGE'],
   
    schedules:['11','15','8','23','14'],
    imageData:[],
    serviceData:{
        service_details:{
            service_type:'',
            location_type:'',
            area_type:'',
            evaluator_note:'',
            estimated_cost:0,
            total_cost:0,
            number_of_cleaners:0,
            cleaning_hours:0
        },
        sections:{},
        customer_id:'',
        customer_details:{
          name:'',
          gender:'',
          email:'',
          mobile_number:'',
          dob:'',
          date_day:'',
          date_month:'',
          date_year:'',
          nationality:'',
          sms_preference:'',
          contact_platform:[]
        },
        address_id:'',
        address_details:{
          governorate:'',
          area:'',
          block:'',
          avenue:'',
          building:'',
          street:'',
          floor:'',
          apartment:''
        },

    },
    sections:
    {
       section_name:'',
       size:'',
       wall_type:'',
       ceiling_type:'',
       cement_residue:false,
       section_cost:'',
       section_net_cost:'',
       keynotes:{}
     },
    
  }
},
mounted(){
// this.getTimeSlots()
},
watch: {
  menu (val) {
    val && setTimeout(() => (this.$refs.picker.activePicker = 'YEAR'))
  },
},
  created: function() {
     
        
    console.log('Vue instance was created');
  },
  methods: {
    getTimeSlots(){
      axios.get('/customer/ajax/getcleaningslotes?service_type='+this.serviceType+'&number_of_cleaners='+1+'&cleaning_date=27-3-2021')
      .then(function (response) {
        console.log(response.data);
        console.log(response.status);
        console.log(response.statusText);
        console.log(response.headers);
        console.log(response.config);
      }).catch(function (error) {
        console.log(error);
      });
    },
    setDuration(hours,cleaners){
      this.duration.push({
        hours:hours,
        cleaners:cleaners
      })
    },
    save (date) {
      this.$refs.menu.save(date)
    },
    onImageFileChanged(event) {
      
      
     
      this.ImageDetails.url = URL.createObjectURL(
        event.target.files[0]
      );
      this.ImageDetails.file = event.target.files[0];
      this.imageData.push(this.ImageDetails);
      this.ImageDetails={
        file:'',
        url:''
      }
     
    },
    deleteImage(imageindex){
      this.imageData.splice(imageindex,1);
    },

    addNew(){
      this.otherService={
        material:'',
        color:'',
        size:'',
        type:'',
        age:'',
        stain:false,
        stain_reason:'',
        wall_type:'',
        floor_type:'',
        ceiling_type:'',
        residue:false,
        hallway_size:'',
        sides:'',
        stain_age:''
      }
      this.dialog=true;
      this.dialogmsg='Add New';
      this.dialogStat=true;
      this.building=[];
    },
    editItem(a,b){
      this.dialog=true;
      this.dialogmsg='Edit'
      this.dialogStat=false;
      this.otherService={
        material:a.material,
        color:a.color,
        size:a.size,
        type:a.type,
        age:a.age,
        stain:a.stain,
        stain_reason:a.stain_reason,
        wall_type:a.wall_type,
        floor_type:a.floor_type,
        ceiling_type:a.ceiling_type,
        residue:a.residue,
        hallway_size:a.hallway_size,
        sides:a.sides,
        stain_age:a.stain_age
      },
      this.currentItem=b;
    },
    saveChanges(){
      this.otherServices[this.currentItem]=this.otherService;
      this.dialog=false
    },
    addOtherService(){
      this.otherServices.push(this.otherService);
      this.otherService={
        material:'',
        color:'',
        size:'',
        type:'',
        age:'',
        stain:false,
        stain_reason:'',
        wall_type:'',
        floor_type:'',
        ceiling_type:'',
        residue:false,
        hallway_size:'',
        sides:'',
        stain_age:''
      }
      this.dialog=false
    },
    deleteItem(a){
      this.otherServices.splice(a,1);

    },
    selectServ(elem) {
      this.billingData=[];
     this.serviceType=elem;
     this.serviceSection.service_type=this.serviceType;
     this.otherServices=[];
     this.no_of_apartments=[];
     this.no_of_floors=[];
     this.no_of_building=0;
     this.otherService={
      material:'',
      color:'',
      size:'',
      type:'',
      age:'',
      stain:false,
      stain_reason:'',
      wall_type:'',
      floor_type:'',
      ceiling_type:'',
      residue:false,
      
      hallway_size:'',
      sides:''
    }
   this.e={
    building:[]
  },
      console.log('service type is'+this.serviceType);
    },
    addSectionFloor(section){
        this.serviceSection.sections[section]={
            size:''
        }
    },
    /*findCost(){
        this.totalCost=0;
        for(var i in this.serviceSection.sections){
          //  console.log("cost is "+this.serviceSection.sections[i].cost);
            this.totalCost=parseInt(this.totalCost)+parseInt(this.serviceSection.sections[i].cost);
        }
    },*/
    setBuilding(){
      for(var i=0;i<this.no_of_building;i++){
        this.building.push(
          {
            floors:[],
            completed:false
          }
        )
        this.e.building.push({
          floors:[],
          e:1,
          
        })
      }
    },
    setFloors(building){
      this.building[building-1].floors=[];
      this.e.building[building-1].e=1;
      for(var i=0;i<this.no_of_floors[building-1];i++){
        this.building[building-1].floors.push(
          
          {
           
            section_name:'',
            size:'',

            wall_type:'',
            ceiling_type:'',
            cement_residue:false,
            section_cost:'',
            section_net_cost:'',
            keynotes:{},
            apartment:false,
            apartments:[],
            completed:false,
            paint_residue:false,
            upholsteries:['Sofa','']

          }
        )
        this.e.building[building-1].floors.push({
          floors:[],
          e:1,
        
        })
      }
      
      
    },
    setApartments(building,floor){
      this.building[building-1].floors[floor-1].apartments=[];
      this.e.building[building-1].floors[floor-1].e=1;
      for(var i=0;i<this.building[building-1].floors[floor-1].no_of_apartments;i++){
        this.building[building-1].floors[floor-1].apartments.push(
          
          {
           
            section_name:'',
            size:'',
            completed:false,
            wall_type:'',
            ceiling_type:'',
            cement_residue:false,
            paint_residue:false,
            section_cost:'',
            section_net_cost:'',
            no_of_rooms:'',
            no_of_bathrooms:'',
            no_of_windows:'',
            keynotes:{},
            

          }
        )
      
      }
      
      
    },
    selectDuration(duration){
        duration.slots=duration.hours/3;
        this.selectedDuration=duration;
       /* this.splitData=[];
        let dur=parseInt(duration);
        var fullDays=0;
        var lastDayHour=0;
        if(dur>10){
            var days=dur/10;
             fullDays=Math.floor(days);
             lastDayHour=days.toString().split('.')[1];
             for(var i=0;i<fullDays;i++){
                this.splitData.push({
                    name:'Day '+(i+1),
                    hours:'10',
                    maxVal:'12',
                    fixed:false
                });
                
            }
            if(lastDayHour>0){
                this.splitData.push({
                    name:'Day '+(i+1),
                    hours:lastDayHour,
                    maxVal:'12',
                    fixed:false
                });
            }


        }
        else{
            this.splitData.push({
                name:'Day ',
                hours:duration,
                maxVal:duration,
                fixed:false
            })
        }
       
       
        console.log("full days is "+fullDays);
        console.log("last day is "+lastDayHour);*/

    },
    nextTab(){
      this.tab='tab2'
      console.log('tab is'+this.tab)
     
    },
    changeDuration(index){
          var currentTotal=0;
          var balCounter=0;
          var lastDay=0;
          this.splitData[index].fixed=true
          for(var i=0;i<this.splitData.length;i++){
             currentTotal=currentTotal+parseInt(this.splitData[i].hours);
          }
         
          var balance = parseInt(this.selectedDuration)-currentTotal;
          console.log("balance is "+balance);
          if (balance>0)
          {
            for(var j=0;j<this.splitData.length;j++){
              if(!this.splitData[j].fixed){
                for (var k=0;k<balance;k++)
                {
                  if(parseInt(this.splitData[j].hours)<10){
                      this.splitData[j].hours=parseInt(this.splitData[j].hours)+1;
                    
                      if(this.splitData[j].hours>=10){
                        this.splitData[j].maxVal=12;
                      }
                      else{
                        this.splitData[j].maxVal=12;
                       
                      }
                      balCounter=balCounter+1;
                     break;
                      
                     
                  }
                  
                }
               
               
              }
            }
            
            var balanceamount=balance-balCounter;
            console.log("balance amount is "+balanceamount);
            if(balanceamount>0){
              var fullDays=0;
              var lastDayHour=0;
              var days=0;
              lastDay=this.splitData.length;
              if(balanceamount>10){
                days=balanceamount/10;
                fullDays=Math.floor(days);
                lastDayHour=days.toString().split('.')[1];
                for(var i=0;i<fullDays;i++){
                  this.splitData.push({
                      name:'Day '+(lastDay+1),
                      hours:'10',
                      maxVal:'12',
                      fixed:false
                  });
                  lastDay=lastDay+1;
                  
              }
              if(lastDayHour>0){
                this.splitData.push({
                    name:'Day '+(lastDay),
                    hours:lastDayHour,
                    maxVal:'12',
                    fixed:false
                });
            }
              }
              else{
                this.splitData.push({
                    name:'Day '+lastDay,
                    hours:balanceamount,
                    maxVal:'12',
                    fixed:false
                })
            }
            }
          }
          else{
            if(balance<0)
            {
            var negBalCounter=0
            for(var j=0;j<this.splitData.length;j++){
              if(!this.splitData[j].fixed){
                for (var k=0;k<(-1*balance);k++)
                {
                  if(parseInt(this.splitData[j].hours)>0){
                      this.splitData[j].hours=parseInt(this.splitData[j].hours)-1;
                      if(this.splitData[j].hours>=10){
                        this.splitData[j].maxVal=12;
                      }
                      else{
                        this.splitData[j].maxVal=12;
                       
                      }
                      negBalCounter=negBalCounter+1;
                      
                     
                     
                  }
                  
                  
                  
                  
                }
               
                
               
              }
              if(negBalCounter==(-1*balance)){
                break;
              }
              else{
                if(negBalCounter==0 && (-1*balance)!=0){
                  for (var m=0;m<(-1*balance);m++)
                  {
                    if((parseInt(this.splitData[j].hours)>0) && j!=index ){
                        this.splitData[j].hours=parseInt(this.splitData[j].hours)-1;
                        if(this.splitData[j].hours>=10){
                          this.splitData[j].maxVal=12;
                        }
                        else{
                          this.splitData[j].maxVal=12;
                         
                        }
                        negBalCounter=negBalCounter+1;
                        
                       
                       
                    }
                    
                    
                    
                    
                  }
                }
              }
            }
            if(balance<0){
              for(var i=0;i<this.splitData.length;i++){
                if(parseInt(this.splitData[i].hours)==0){
                  this.splitData.splice(i,1);
                }
               
              }
            }
          }
          }
       
    },
    parseSize(){
      this.sizeData=[]
      for(var i in this.serviceSize){
          this.serviceSize[i]['combinedSize']=this.serviceSize[i].name+'( '+this.serviceSize[i].min_size+' sq. m - '+this.serviceSize[i].max_size+' sq. m )';
          this.sizeData.push(this.serviceSize[i]);
      }
    },
    nextApartment(building,floor,apartment){
      this.e.building[building].floors[floor].e = (apartment+2)
      this.building[building].floors[floor].apartments[apartment].completed=true
      var itemFound=false
      for (var i=0;i<this.billingData.length;i++){
          if(this.billingData[i].name=='Building '+(building+1)+' Floor '+(floor+1)+' Apartment '+(apartment+1)){
            itemFound=true
            this.billingData[i].section=this.building[building].floors[floor].apartments[apartment]
          }
      }
      if(!itemFound){
        this.billingData.push({
          name:'Building '+(building+1)+' Floor '+(floor+1)+' Apartment '+(apartment+1),
          section:this.building[building].floors[floor].apartments[apartment]
      })
      }
      
      this.recalcPrice()
    },
    nextFloor(building,floor){
      this.e.building[building].e = (floor+1)
      this.building[building].floors[floor-1].completed=true
      var floorFound=false
      for (var i=0;i<this.billingData.length;i++){
        if(this.billingData[i].name=='Building '+(building+1)+' Floor '+(floor)){
          floorFound=true
          this.billingData[i].section=this.building[building].floors[floor-1]
        }
    }
    if(!floorFound)
    {
      if(!this.building[building].floors[floor-1].apartment){
      this.billingData.push({
          name:'Building '+(building+1)+' Floor '+(floor),
          section:this.building[building].floors[floor-1]
      })
      if(floor==this.building[building].floors.length){
        this.building[building].completed=true;
        console.log("floor is "+floor)
      }
      
    }
  }
    this.recalcPrice()
   
    },
    recalcPrice(){
      this.totalCost=0;
      for(var i=0;i<this.billingData.length;i++){
        this.totalCost=this.totalCost+this.billingData[i].section.size.cost
      }
    },
    setCost(building,floor,apartment){
      this.building[building].floors[floor].apartments[apartment].cost=''
    }
  },
  
})
Vue.use(Vuetify);

//app.exampleFunction();







durationcalculation();
var generalCleaningSize = {};
var deepCleaningSize = {};
var storageAreaCleaningSize = {};

var noOfBuildings = 0;
var buildingData = [];
var serviceData = {
  location_type: '',
  area_type: '',
  building: [],
  schedule: {},
  address: {}
}
var sectionData = {
  location_type: '',
  area_type: '',
  size: '',
  sections: {},


}
var floorCount = 0;
var currentFloor = 1;
var buildingNumber = 0;
var cleaningType = '';
var location_type = '';
var area_type = '';
var itemCount = 0;
var sofaCount = 0;
var materialSelectBox = [];
var colorSelectBox = [];
var sizeSelectBox = [];
var reasonSelectBox = [];
var floorSelectBox = [];
var wallSelectBox = [];
var ceilingSelectBox = [];
var sizeSelectBox = [];
var hallwaySelectBox = [];
var sidesSelectBox = [];
var items = [];

$('.tabset').hide();
//let mySelect = new vanillaSelectBox("#area-type", { placeHolder: "Area Type" });
//let mySelect2 = new vanillaSelectBox("#location-type", { placeHolder: "Location Type" });
$('.inv-check-icon').hide()



$('.mc-display__body').replaceWith('<h6 class="text-center mt-2">Available Slots</h6><div class="row w-100 mt-2"><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 10 : 00am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 11 : 00 am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 01 : 00 pm </div> </div></div>');

//let noOfBuilding = new vanillaSelectBox("#no-of-buildings", { placeHolder: "No of buildings" });


$('#tab-1-content').show();
function activateTab(elem) {
  var elementId = $(elem).attr('id');
  var activeTab = $('.sr-tabs').find(".sr-tab-active");
  var activeElem = $(activeTab).attr('id');
  console.log("active is " + activeElem);
  $('.tab-content').hide();
  $('#' + elementId + '-content').show();
  $('#' + activeElem).removeClass("sr-tab-active");
  $('#' + activeElem).addClass("sr-tab");
  $('#' + elementId).removeClass("sr-tab");
  $('#' + elementId).addClass('sr-tab-active');

}
$(document).ready(function () {
  $('.owl-carousel').owlCarousel(
      {

          loop: true,
          margin: 10,
          dots: true,

          responsiveClass: true,

          responsive: {
              0: {
                  items: 1,

                  stagePadding: 50,
              },
              600: {
                  items: 4,

                  dots: true,
                 
                  

              },
              1000: {
                  items: 4,

                  loop: false,
                  

              }
          }
      }
  );
});
function nextTab(elem){
  var elid=$(elem).attr('id');
  console.log('tab is'+'#tab'+elid.split('-')[1]);
  if(parseInt(elid.split('-')[1])==app.building.length){
    app.buildingsCompleted=true;
  }
  else{
    $('#tab'+(parseInt(elid.split('-')[1])+1)).click();
  }
  app.e.building[(parseInt(elid.split('-')[1])-1)].e=app.building.length+1;
  
  
}
function getSlot() {
  console.log("yes i run")
  $('.mc-display__body').replaceWith('<div class="row w-100"><div class="col-md-6 "><div class="time-slot"> 10 : 00am </div> </div><div class="col-md-6 "><div class="time-slot"> 11 : 00 am </div> </div></div>');
}
$(document).on('click', '.mc-date', function () {
  $('.mc-display__body').replaceWith('<h6>Time Slot</h6><div class="row w-100 mt-4"><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 10 : 00am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 11 : 00 am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 01 : 00 pm </div> </div></div>');

});
function selectPayment(pay){
if(pay=='debit')
{
 $("#inv-debit").removeClass('inv-payment-card')
 $("#inv-debit").addClass('inv-payment-card-active')
 $("#inv-cash").removeClass('inv-payment-card-active')
 $("#inv-cash").addClass('inv-payment-card')
 $("#inv-credit").removeClass('inv-payment-card-active')
 $("#inv-credit").addClass('inv-payment-card')
 $("#inv-check-debit").show();
 $("#inv-check-credit").hide();
 $("#inv-check-cash").hide();
 $("#inv-debit-check-box").addClass('inv-check-box-active');
 $("#inv-cash-check-box").removeClass('inv-check-box-active');
 $("#inv-credit-check-box").removeClass('inv-check-box-active');
/* $("#inv-knet").attr("src","./icons/knet-white.png");
 $("#inv-cash-img").attr("src","./icons/wallet.png");
 $("#inv-credit-img").attr("src","./icons/debit-card.png");*/

}
else{
  if(pay=='cash'){
   $("#inv-cash").removeClass('inv-payment-card')
   $("#inv-debit").removeClass('inv-payment-card-active')
   $("#inv-debit").addClass('inv-payment-card')
   $("#inv-cash").addClass('inv-payment-card-active')
   $("#inv-credit").removeClass('inv-payment-card-active')
   $("#inv-credit").addClass('inv-payment-card');
  /* $("#inv-knet").attr("src","./icons/knet-icon.png");
   $("#inv-cash-img").attr("src","./icons/wallet-white3.png");
   $("#inv-credit-img").attr("src","./icons/debit-card.png");*/
   $("#inv-check-cash").show();
   $("#inv-check-debit").hide();
 $("#inv-check-credit").hide();
 $("#inv-cash-check-box").addClass('inv-check-box-active');
 $("#inv-debit-check-box").removeClass('inv-check-box-active');
 $("#inv-credit-check-box").removeClass('inv-check-box-active');
  }
  else{
   $("#inv-credit").removeClass('inv-payment-card')
   $("#inv-debit").removeClass('inv-payment-card-active')
   $("#inv-debit").addClass('inv-payment-card')
   $("#inv-credit").addClass('inv-payment-card-active')
   $("#inv-cash").removeClass('inv-payment-card-active')
 $("#inv-cash").addClass('inv-payment-card')
 $("#inv-check-credit").show();
 $("#inv-check-debit").hide();
 $("#inv-check-cash").hide();
 $("#inv-credit-check-box").addClass('inv-check-box-active');
 $("#inv-debit-check-box").removeClass('inv-check-box-active');
 $("#inv-cash-check-box").removeClass('inv-check-box-active');
/* $("#inv-knet").attr("src","./icons/knet-icon.png");
 $("#inv-cash-img").attr("src","./icons/wallet.png");
 $("#inv-credit-img").attr("src","./icons/credit-card-white.png");*/
  }

}
}
function activeSlot(ele) {

  console.log("element is " + ele);
  $('.time-slot').removeClass('time-slot-active');
  $(ele).addClass('time-slot-active');
}
function getSize(srvc) {
  
  axios.get('/customer/ajax/getservicesizeprice?service_type=' + srvc)
      .then(function (response) {
          console.log(response);
          if (srvc == 'General Cleaning') {
              generalCleaningSize = response.data;

              app.serviceSize = response.data;

              app.parseSize();
              console.log("general clenainhg sise is " + JSON.stringify(generalCleaningSize));
          }

          else {
              if (srvc == 'Deep Cleaning') {
                  deepCleaningSize = response.data;
                  app.serviceSize = response.data;
                  app.parseSize();
                  console.log("deep clenainhg sise is " + JSON.stringify(deepCleaningSize));
              }
              else {
                  if (srvc == 'Storage Area') {
                      storageAreaCleaningSize = response.data;
                      app.serviceSize = response.data;
                      app.parseSize();
                      console.log("storage clenainhg sise is " + JSON.stringify(storageAreaCleaningSize));
                  }
              }
          }

      })
      .catch(function (error) {
          console.log(error);
      })
      .then(function () {
          // always executed
      });
}
function selectService(elem) {
  $('#location-type').val('Location Type');
  $('.building').hide();
  $('.common-field').hide();
  $('.sr-tab-marker').remove();
  $('.tab-panel').remove();
  noOfBuildings = 0;
  buildingData = [];
  floorCount = 0;
  currentFloor = 1;
  buildingNumber = 0;
  
  $('.questions').show();
  $('.sr-service-card-active').addClass('sr-service-card');
  $('.sr-service-card-active').removeClass('sr-service-card-active');
  $(elem).addClass('sr-service-card-active');
  $(elem).removeClass('sr-service-card');
  $('.select-icon').removeClass('fa');
  $('.select-icon').removeClass('fa-check-circle');
  $('.select-icon').addClass('far');
  $('.select-icon').addClass('fa-circle');
  $('.select-icon').addClass('inactive-icon');
  $('.select-icon').removeClass('select-icon');
  $(elem).find('i').removeClass('far');
  $(elem).find('i').removeClass('fa-circle');
  $(elem).find('i').removeClass('inactive-icon');
  $(elem).find('i').addClass('fa');

  $(elem).find('i').addClass('fa-check-circle');
  $(elem).find('i').addClass('select-icon');
  cleaningType = $(elem).find('.service-title').text();
  app.selectServ(cleaningType);
    getSize(cleaningType);
   


}

function durationcalculation(params)
{
// selected_service = $("#bk-service option:selected" ).text();
selected_service     = 'General Cleaning';

$.ajax({

    url: "/customer/ajax/getserviceproductivity",

    data: {'service_type':selected_service}, 

    dataType: 'json',

    success: function (data) {
        console.log(data);      
        //to find total size and manhour
        if(selected_service == 'Upholstery Cleaning')
        {
          total_sofa_size    = 6;
          total_chair_size   = 9;
          total_curtain_size = 750;
          manhour = parseInt(total_sofa_size/data['sofa_perhour_cleaning'])+parseInt(total_chair_size/data['chair_perhour_cleaning'])+parseInt(total_curtain_size/data['curtain_perhour_cleaning'])
        }

        else if(selected_service == 'Facade Cleaning')
        {
          total_highpricefacade_size = 400;
          total_lowpricefacade_size  = 400;
          manhour = parseInt(total_highpricefacade_size/data['highpricefacade_perhour_cleaning'])+parseInt(total_lowpricefacade_size/data['lowpricefacade_perhour_cleaning'])
        }

        else if(selected_service == 'Kitchen Cleaning')
        {
          total_newkitchen_size = 400;
          total_oldkitchen_size  = 400;
          manhour = parseInt(total_newkitchen_size/data['newkitchen_perhour_cleaning'])+parseInt(total_oldkitchen_size/data['oldkitchen_perhour_cleaning'])
        }

        else if(selected_service == 'Window Cleaning')
        {
          total_highpricewindow_size = 400;
          total_lowpricewindow_size  = 400;
          manhour = parseInt(total_highpricewindow_size/data['highpricewindow_perhour_cleaning'])+parseInt(total_lowpricewindow_size/data['lowpricewindow_perhour_cleaning'])
        }

        else
        {
          total_estimated_size = 100;
          productivity         = data['perhour_cleaning'];
          manhour              = parseInt(total_estimated_size/productivity)
        }

        //optimal finding
        r       = 2 ** (manhour.toString().length-1)
        mod     = manhour%r
        
        if (mod > parseInt(r/2))
        {
          n= manhour+(r-mod);
        }
        else
        {
          n = manhour-mod;
        }
        console.log(manhour,"manhour")
        console.log(r,"r")
        console.log(mod,"mod")
        console.log(n,"n")
        var pair=[]
        for(var i=1;i<parseInt(n ** (1/2))+1;i++)
        {
          if(n%i == 0)
            {
              pair = [i,n/i];
            }
        }
        console.log(pair,"pair");
        //pair convert to 3's multiple
        convertion_r       = 3
        convertion_mod     = pair[1]%convertion_r
        
        if (convertion_mod > parseInt(convertion_r/3))
        {
          console.log(manhour,"divider")
          console.log((pair[1]+(convertion_r-convertion_mod)),"divident")
          console.log(parseInt(manhour/(pair[1]+(convertion_r-convertion_mod))),"division")
          pair = [Math.round(manhour/(pair[1]+(convertion_r-convertion_mod))),(pair[1]+(convertion_r-convertion_mod))];
        }
        else
        {
          console.log(manhour,"divider")
          console.log((pair[1]-convertion_mod),"divident")     
          
          if((pair[1]-convertion_mod) == 0)
          {
            pair = [Math.round(manhour/3),3];
          }
          else
          {
            pair = [Math.round(manhour/(pair[1]-convertion_mod)),(pair[1]-convertion_mod)];
          }
        }


        console.log(pair,"newpair")

        max_cleaners = data['max_cleaners']
        //max_cleaners=10;
        duration_list  = [];
        lower_loop     = 0;
        upper_loop     = 0;
        middle_element = pair[0];
        middle_hours   = pair[1];

        if(middle_element<=max_cleaners && middle_element>0)
        {
          duration_list.push(pair);

          //first
          if(Math.round(manhour/(middle_hours-3))>0 && Math.round(manhour/(middle_hours-3)) <= max_cleaners)
            {
              duration_list.push([Math.round(manhour/(middle_hours-3)),(middle_hours-3)]);
              lower_loop = 1;
            }
          if(Math.round(manhour/(middle_hours+3))>0 && Math.round(manhour/(middle_hours+3))<=max_cleaners)
            {
              duration_list.push([Math.round(manhour/(middle_hours+3)),(middle_hours+3)]); 
              upper_loop = 1;
            }

          //check
          if(Math.round(manhour/(middle_hours-6))>0 && Math.round(manhour/(middle_hours-6)) <= max_cleaners && upper_loop == 0)
            {
              duration_list.push([Math.round(manhour/(middle_hours-6)),(middle_hours-6)]); 
              lower_loop = 1;
            }
          if(Math.round(manhour/(middle_hours+6))>0 && Math.round(manhour/(middle_hours+6))<=max_cleaners && lower_loop == 0)
            { 
              duration_list.push([Math.round(manhour/(middle_hours+6)),(middle_hours+6)]);
              upper_loop = 1;
            }
        }

        else if(middle_element == 0 && max_cleaners > 0)
        {
          //1st
          duration_list.push([1,middle_hours]);

          //2nd
          if(Math.round(manhour/(middle_hours+3)) > 0 && Math.round(manhour/(middle_hours+3)) <= max_cleaners)
          {
            duration_list.push([Math.round(manhour/(middle_hours+3)),(middle_hours+3)]);  
          }
          else
          {
            duration_list.push([1,(middle_hours+3)]); 
          }

          //3rd
          if(Math.round(manhour/(middle_hours+6)) > 0 && Math.round(manhour/(middle_hours+6)) <= max_cleaners)
          {
            duration_list.push([Math.round(manhour/(middle_hours+6)),(middle_hours+6)]);  
          }
          else
          {
           duration_list.push([1,(middle_hours+6)]); 
          }

        }

        else
        {
          middle_element = max_cleaners;
          middle_hours   = Math.round(manhour/middle_element)-((Math.round(manhour/middle_element))%3)
          if(middle_hours == 0)
          {
           middle_hours = 3; 
          } 

          //1st
          duration_list.push([middle_element,middle_hours])
          
          //2nd
          if(Math.round(manhour/(middle_hours+3)) > 0 && Math.round(manhour/(middle_hours+3)) <= max_cleaners)
          {
            duration_list.push([Math.round(manhour/(middle_hours+3)),(middle_hours+3)]);  
          }
          else
          {
            duration_list.push([middle_element,(middle_hours+3)]); 
          }

          //3rd
          if(Math.round(manhour/(middle_hours+6)) > 0 && Math.round(manhour/(middle_hours+3)) <= max_cleaners)
          {
            duration_list.push([Math.round(manhour/(middle_hours+6)),(middle_hours+6)]);  
          }
          else
          {
           duration_list.push([middle_element,(middle_hours+6)]); 
          }
            
          
        }
        console.log(duration_list)

        for(i=0;i<duration_list.length;i++)
          {
            
            total_duration  = duration_list[i][1];
            //show to users
            total_minutes     = (total_duration.toFixed(2)*60).toFixed(0)
            converted_hours   = Math.floor(total_minutes / 60);          
            converted_minutes = total_minutes % 60;
            total_cleaners    = duration_list[i][0];
            console.log(converted_hours,"converted_hours")
            console.log(converted_minutes,"converted_minutes")
            console.log(total_cleaners,"total_cleaners")
            app.setDuration(converted_hours,total_cleaners);

            }
               }
     });


}
