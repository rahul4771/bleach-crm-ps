

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
    ImageDetails:{
      url:'',
      file:''
    },
    images: [],
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
    sides:''
  },
  color:['Blue','Yellow','Orange','Red','Black','White'],
  material:['Material 1','Material 2','Material 3','Material 4'],
  upholsteryType:['Sofa','Chair','Curtain'],
  upholsterySize1:['Small','Medium','Large','Xtra Large'],
  upholsterySize2:['Small','Medium','Large'],
  upholsterySize3:['Small','Medium','Large'],
  tab:'',
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
        
        sections:{

        }
    }
    
  }
},
  created: function() {
     
        
    console.log('Vue instance was created');
  },
  methods: {

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
        sides:''
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
        sides:a.sides
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
        sides:''
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
           
          }
        )
        this.e.building.push({
          floors:[],
          e:1
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
        this.selectedDuration=duration;
        this.splitData=[];
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
        console.log("last day is "+lastDayHour);

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
      this.building[building].floors[floor].apartments[apartment].completed=true,
      this.billingData.push({
        name:'Building '+(building+1)+' Floor '+(floor+1)+' Apartment '+(apartment+1),
        section:this.building[building].floors[floor].apartments[apartment]
    })
    this.totalCost=this.totalCost+this.building[building].floors[floor].apartments[apartment].size.cost
    },
    nextFloor(building,floor){
      this.e.building[building].e = (floor+1)
      this.building[building].floors[floor-1].completed=true
      if(!this.building[building].floors[floor-1].apartment){
      this.billingData.push({
          name:'Building '+(building+1)+' Floor '+(floor),
          section:this.building[building].floors[floor-1]
      })
      this.totalCost=this.totalCost+this.building[building].floors[floor-1].size.cost
    }
    },
    setCost(building,floor,apartment){
      this.building[building].floors[floor].apartments[apartment].cost=''
    }
  },
  
})
Vue.use(Vuetify);

//app.exampleFunction();








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
                  items: 3,

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
