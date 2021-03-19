/* Vue js */


    var app = new Vue({
      el: '#app',
      delimiters: ["<%","%>"],
      data () {
      return {
      service:'test',
        serviceType:'',
        serviceSection:{
            service_type:'',
            area_type:'',
            location_type:'',
            sections:{

            }
        },
        splitData:['8'],
        selectTest:'',
        selectedDuration:'8',
        size:'',
        totalCost:0,
        schedules:['11','15','8','23','14']
        
      }
  },
      created: function() {
        console.log('Vue instance was created');
      },
      methods: {
        selectServ(elem) {
         this.serviceType=elem;
         this.serviceSection.service_type=this.serviceType;
          console.log('service type is'+this.serviceType);
        },
        addSectionFloor(section){
            this.serviceSection.sections[section]={
                size:''
            }
        },
        findCost(){
            this.totalCost=0;
            for(var i in this.serviceSection.sections){
              //  console.log("cost is "+this.serviceSection.sections[i].cost);
                this.totalCost=parseInt(this.totalCost)+parseInt(this.serviceSection.sections[i].cost);
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
           
        }
      },
      /*destroyed: function() {
        console.log('Vue instance was destroyed');
      }*/
    })
  
    //app.exampleFunction();
  
  






getSize('General Cleaning');
var generalCleaningSize={};
var deepCleaningSize={};
var storageAreaCleaningSize={};

var noOfBuildings=0;
var buildingData=[];
var serviceData={
    location_type:'',
    area_type:'',
    building:[],
    schedule:{},
    address:{}
}
var sectionData={
    location_type:'',
    area_type:'',
    size:'',
    sections:{},

    
}
var floorCount=0;
var currentFloor=1;
var buildingNumber=0;
var cleaningType='';
var location_type='';
var area_type='';
var itemCount=0;
var sofaCount=0;
var materialSelectBox=[];
var colorSelectBox=[];
var sizeSelectBox=[];
var reasonSelectBox=[];
var floorSelectBox=[];
var wallSelectBox=[];
var ceilingSelectBox=[];
var sizeSelectBox=[];
var hallwaySelectBox=[];
var sidesSelectBox=[];
var items=[];

$('.tabset').hide();
let mySelect = new vanillaSelectBox("#area-type",{placeHolder: "Area Type"});
let mySelect2 = new vanillaSelectBox("#location-type",{placeHolder: "Location Type"});
let mySelect3 = new vanillaSelectBox("#wall-type",{placeHolder: "Wall Type"});
let mySelect4 = new vanillaSelectBox("#size",{placeHolder: "Size"});
let mySelect5 = new vanillaSelectBox("#hallway-size",{placeHolder: "Hallway Size"});
let mySelect6 = new vanillaSelectBox("#floor-type",{placeHolder: "Floor Type"});
let mySelect7 = new vanillaSelectBox("#ceiling-type",{placeHolder: "Ceiling Type"});
let mySelect8 = new vanillaSelectBox("#rack-type",{placeHolder: "Rack Type"});

/*let materialSelect = new vanillaSelectBox("#material",{placeHolder: "Choose Material"});
let mySelect2_1 = new vanillaSelectBox("#color-2",{placeHolder: "Location Type"});
let materialSelect2 = new vanillaSelectBox("#material-2",{placeHolder: "Choose Material"});
let mySelect3 = new vanillaSelectBox("#color-3",{placeHolder: "Location Type"});
let materialSelect3 = new vanillaSelectBox("#material-3",{placeHolder: "Choose Material"});
//let mySelect3 = new vanillaSelectBox("#duration",{placeHolder: "Duration"});*/

$('.mc-display__body').replaceWith('<h6 class="text-center mt-2">Available Slots</h6><div class="row w-100 mt-2"><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 10 : 00am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 11 : 00 am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 01 : 00 pm </div> </div></div>');

let noOfBuilding = new vanillaSelectBox("#no-of-buildings",{placeHolder: "No of buildings"});
//let noOfFloors = new vanillaSelectBox("#no-of-floors",{placeHolder: "No of Floors"});

$('#tab-1-content').show();
function activateTab(elem){
    var elementId=$(elem).attr('id');
    var activeTab=$('.sr-tabs').find(".sr-tab-active");
    var activeElem=$(activeTab).attr('id');
    console.log("active is "+activeElem);
    $('.tab-content').hide();
    $('#'+elementId+'-content').show();
    $('#'+activeElem).removeClass("sr-tab-active");
    $('#'+activeElem).addClass("sr-tab");
    $('#'+elementId).removeClass("sr-tab");
   $('#'+elementId).addClass('sr-tab-active');

}
$(document).ready(function(){
    $('.owl-carousel').owlCarousel(
        {
            
            loop:true,
            margin:10,
            dots:true,
            
            responsiveClass:true,
           
            responsive:{
                0:{
                    items:1,
                   
                    stagePadding: 50,
                },
                600:{
                    items:3,
                   
                    dots:true,
                    
                },
                1000:{
                    items:4,
                  
                    loop:false,
                    
                }
            }
        }
    );
  });
  function getSlot(){
      console.log("yes i run")
      $('.mc-display__body').replaceWith('<div class="row w-100"><div class="col-md-6 "><div class="time-slot"> 10 : 00am </div> </div><div class="col-md-6 "><div class="time-slot"> 11 : 00 am </div> </div></div>');
  }
  $(document).on('click','.mc-date',function(){
    $('.mc-display__body').replaceWith('<h6>Time Slot</h6><div class="row w-100 mt-4"><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 10 : 00am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 11 : 00 am </div> </div><div class="col-6 pt-2"><div class="time-slot" onclick="activeSlot(this)"> 01 : 00 pm </div> </div></div>');

});
function activeSlot(ele){
    //elem.addClass('time-slot-active');
    console.log("element is "+ele);
    $('.time-slot').removeClass('time-slot-active');
    $(ele).addClass('time-slot-active');
}
function addTabs(){
   
    for(var j=noOfBuildings;j>0;j--){
        $('#tab'+j).remove();
        $('#tab-label-'+j).remove();
      
       
    }
   noOfBuildings=parseInt($('#no-of-buildings').val());
       
        $('.tabset').show();
     
    for(var i=noOfBuildings;i>0;i--){
        $('.tabset').prepend('<input type="radio" name="tabset" class="sr-tab-marker" id="tab'+i+'" aria-controls="tab-building-'+i+'" checked onclick="switchTab('+i+')"><label id="tab-label-'+i +'" for="tab'+i+'" class="sr-tab-marker">Building '+i+'</label> ');
        $('.tab-panels').prepend(`<section id="tab-building-`+i+`" class="tab-panel">
        <div class="row" id="floors-count-`+i+`">
            <div class="col-md-4" >
            <select id="no-of-floors-`+i+`" onchange="addFloors(this)" >
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
            </select> 
            </div>
           
            </div>
            </section`);
        let Floors = new vanillaSelectBox("#no-of-floors-"+i,{placeHolder: "No of Floors"});
       
        buildingData.push({
            building:'building-'+(noOfBuildings-i+1),
            floors:[]

        });
        serviceData.building.push({
            building:'building-'+(noOfBuildings-i+1),
            floors:[],
        

        });
    }
   

   
}
function addFloors(elem){
    
  if(elem){
    
      floorCount=$(elem).val();
       buildingNumber=$(elem).attr('id').split('-')[3];
       currentFloor=1;
       
      
  }
  else{
      floorCount=$('#no-of-floors-'+buildingNumber).val();
      console.log("i m here");
      var prevFloor=currentFloor-1;
      let floor_size=$('#floor-'+buildingNumber+"-"+prevFloor+'-size').val();
      let noOfRooms=$('#floor-'+buildingNumber+"-"+prevFloor+'-room').val();
      let wallType=$('#floor-'+buildingNumber+"-"+prevFloor+'-walltype').val();
      let ceilingType=$('#floor-'+buildingNumber+"-"+prevFloor+'-ceilingType').val();
      let noOfBathrooms=$('#floor-'+buildingNumber+"-"+prevFloor+'-bathroom').val();
      let noOfWindows=$('#floor-'+buildingNumber+"-"+prevFloor+'-window').val();
      let noOfApartments=$('#floor-'+buildingNumber+'-'+prevFloor+'-no-of-apartment').val();
      buildingData[buildingNumber-1].floors.push({
          floor:prevFloor,
          size:floor_size,
          room:noOfRooms,
          apartments:[]
      });
      serviceData.building[buildingNumber-1].floors.push({
          floor:prevFloor,
          size:floor_size,
          wall_type:wallType,
          ceiling_type:ceilingType,
          no_of_bathrooms:noOfBathrooms,
          no_of_windows:noOfWindows,
          no_of_rooms:noOfRooms,
          apartments:[]
      })
      console.log("no of apart is "+noOfApartments);
      if(noOfApartments>0){
          for(var i=1;i<=noOfApartments;i++){
               floor_size=$('#apartment-'+buildingNumber+"-"+prevFloor+'-'+i+'-size').val();
               noOfRooms=$('#apartment-'+buildingNumber+"-"+prevFloor+'-'+i+'-room').val();
               wallType=$('#apartment-'+buildingNumber+"-"+prevFloor+'-'+i+'-walltype').val();
               ceilingType=$('#apartment-'+buildingNumber+"-"+prevFloor+'-'+i+'-ceilingType').val();
               noOfBathrooms=$('#apartment-'+buildingNumber+"-"+prevFloor+'-'+i+'-bathroom').val();
               noOfWindows=$('#apartment-'+buildingNumber+"-"+prevFloor+'-'+i+'-window').val();
               noOfApartments=$('#apartment-'+buildingNumber+'-'+prevFloor+'-'+i+'-no-of-apartment').val();
              serviceData.building[buildingNumber-1].floors[prevFloor-1].apartments.push({
                  size:floor_size,
                  wall_type:wallType,
                  ceiling_type:ceilingType,
                  no_of_bathrooms:noOfBathrooms,
                   no_of_windows:noOfWindows,
                   no_of_rooms:noOfRooms,
              })
          }
      }
     
      
      console.log("service data is "+JSON.stringify(serviceData));
      $('#floors-count-'+buildingNumber).append(`
      <div class="floors-card mt-4 mb-2 col-md-12" id="floor-result-`+buildingNumber+`-`+prevFloor+`">
       <div class="row">
          <div class="col-md-8">
              <div class="p-2">
                  <div class="sr-sub-heading">
                     Floor
                  </div>
                  <div id="result-floor-`+buildingNumber+`-`+prevFloor+`">
                     Floor `+prevFloor+`
                  </div>
              </div>
          </div>
          
         
         
          <div class="col-md-4">
              <div class="p-2"><div class="sr-sub-heading">
                 Actions
              </div>
              <div>
                  <i class="far fa-edit edit-icon" id="edit-`+buildingNumber+`-`+prevFloor+`" onclick="editFloor(this)"></i>
                  <i class="far fa-trash-alt pl-2 del-icon" id="delete-`+buildingNumber+`-`+prevFloor+`" onclick="deleteFloor(this)"></i>
              </div>
          </div>
          </div>
          </div>
      </div>
     
  </div>
      `);
      $('#floor-'+buildingNumber+"-"+prevFloor).hide();
  }
  
  if(buildingData[buildingNumber-1].floors.length>0){
      currentFloor=buildingData[buildingNumber-1].floors.length+1;
  }
  
 
/* <div class="col-md-3">
              <div class="p-2"><div class="sr-sub-heading">
                  No of rooms
              </div>
              <div id="result-floor-room-`+buildingNumber+`-`+prevFloor+`">`
              +floor_room+
             ` </div>
          </div>
          
            <div class="col-md-5 ">
          <div class="form-group m-2">
              <input type="number" required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-room"/>
              <label for="input" class="control-label" >No of Rooms</label><i class="bar"></i>
            </div>
          
          
      </div>
          */
  
  if(currentFloor<=floorCount){
    Vue.set(app.serviceSection.sections,'Building'+buildingNumber+'Floor'+currentFloor,{keynotes:{},size:'',cost:''});
   // app.addSectionFloor('Building'+buildingNumber+'Floor'+currentFloor);
 if($('#floor-'+buildingNumber+'-'+currentFloor).length==0){
  $('#'+'tab-building-'+buildingNumber).append(`<div class="floor-card mt-4" id="floor-`+buildingNumber+`-`+currentFloor+`">
  <div class="p-2"><h5 class="text-center">Floor `+currentFloor+`</h5></div>
  <div class="row">
  <div class="col-md-5 offset-md-1  mt-2">
          <div class="m-2">
          <h6 >Any Apartments ?</h6>
          <div class="form-radio d-flex">
             
              <div class="radio">
                <label>
                  <input type="radio" name="floor-`+buildingNumber+`-`+currentFloor+`-apartment" value="yes" onclick="apartmentStat(this)"/><i class="helper"></i>Yes
                </label>
              </div>
              <div class="radio ml-4">
                <label>
                  <input type="radio" name="floor-`+buildingNumber+`-`+currentFloor+`-apartment" checked="checked" value="no" onclick="apartmentStat(this)"/><i class="helper"></i>No
                </label>
              </div>
            </div>
            </div>
          
          
      </div>
      <div class="col-md-5 mt-4 floor-option-`+buildingNumber+`-`+currentFloor+`">
          
            <div class="form-group m-2 ">
      <select required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-size" name="floor-`+buildingNumber+`-`+currentFloor+`-size"  onchange="setSize(this,'Floor',`+buildingNumber+`,`+currentFloor+`,0)" >
       
      
      </select>
      <label for="select" class="control-label">Size</label><i class="bar"></i>
    </div>
         
      </div>
      <div class="col-md-5  offset-md-1 mt-2 floor-option-`+buildingNumber+`-`+currentFloor+`">
          
            <div class="form-group m-2 ">
      <select required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-walltype" name="floor-`+buildingNumber+`-`+currentFloor+`-walltype" onchange="setWallType(this,'Floor',`+buildingNumber+`,`+currentFloor+`,0)" >
        <option> Small</option>
        <option>Medium</option>
        <option>Large</option>
      
      </select>
      <label for="select" class="control-label">Wall Type</label><i class="bar"></i>
    </div>
         
      </div>
      <div class="col-md-5  mt-2 floor-option-`+buildingNumber+`-`+currentFloor+`">
          
            <div class="form-group m-2 ">
      <select required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-floortype" name="floor-`+buildingNumber+`-`+currentFloor+`-floortype" onchange="setFloorType(this,'Floor',`+buildingNumber+`,`+currentFloor+`,0)" >
        <option> Small</option>
        <option>Medium</option>
        <option>Large</option>
      
      </select>
      <label for="select" class="control-label">Floor Type</label><i class="bar"></i>
    </div>
         
      </div>
      <div class="col-md-5  mt-2 offset-md-1 floor-option-`+buildingNumber+`-`+currentFloor+`">
          
            <div class="form-group m-2 ">
      <select required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-ceilingtype" name="floor-`+buildingNumber+`-`+currentFloor+`-ceilingtype" onchange="setCeilingType(this,'Floor',`+buildingNumber+`,`+currentFloor+`,0)" >
        <option> Small</option>
        <option>Medium</option>
        <option>Large</option>
      
      </select>
      <label for="select" class="control-label">Ceiling Type</label><i class="bar"></i>
    </div>
         
      </div>
      <div class="col-md-5  mt-2  storage-fields floor-option-`+buildingNumber+`-`+currentFloor+`">
          
      <div class="form-group m-2 ">
<select required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-racktype" name="floor-`+buildingNumber+`-`+currentFloor+`-racktype"  >
  <option> Wooden</option>
  <option>Metal</option>
  <option>Concrete</option>

</select>
<label for="select" class="control-label">Rack Type</label><i class="bar"></i>
</div>
   
</div>
<div class="col-md-5  mt-2 offset-md-1 storage-fields floor-option-`+buildingNumber+`-`+currentFloor+`">
<div class="form-group m-2">
    <input type="number" required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-racks"/>
    <label for="input" class="control-label" >No of Racks</label><i class="bar"></i>
  </div>


</div>   
     
  <div class="col-md-5  mt-2 floor-option-`+buildingNumber+`-`+currentFloor+`">
      <div class="form-group m-2">
          <input type="number" required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-room" v-model="selectTest"/>
          <label for="input" class="control-label" >No of Rooms</label><i class="bar"></i>
        </div>
      
      
  </div>
  <div class="col-md-5 mt-2 offset-md-1 floor-option-`+buildingNumber+`-`+currentFloor+`">
  <div class="form-group m-2">
      <input type="number" required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-bathroom"/>
      <label for="input" class="control-label" >No of Bathrooms</label><i class="bar"></i>
    </div>
  
  
</div>
<div class="col-md-5   mt-2 floor-option-`+buildingNumber+`-`+currentFloor+`">
<div class="form-group m-2">
  <input type="number" required="required" id="floor-`+buildingNumber+`-`+currentFloor+`-window"/>
  <label for="input" class="control-label" >No of Windows</label><i class="bar"></i>
</div>


</div>
      <div class="col-md-5 offset-md-1 mt-2  apartment-count" id="apartment-count-`+buildingNumber+`-`+currentFloor+`">
          <div class="form-group m-2 mt-4">
              <select id="floor-`+buildingNumber+`-`+currentFloor+`-no-of-apartment" name="floor-`+buildingNumber+`-`+currentFloor+`-no-of-apartment" onchange="addApartment(this)"  >
                <option> 1</option>
                <option>2</option>
                <option>3</option>
                <option>4</option>
              </select>
              <label for="select" class="control-label">No of Apartments</label><i class="bar"></i>
            </div>
      </div>
      
      
     
      
  </div>
<div  class="apartments" id="apartment-`+buildingNumber+`-`+currentFloor+`">
 
  </div>

  <div class="row mt-2 mb-2">
      <div class="col-md-12 text-center mb-2">
          <button class="sr-next-btn" onclick="addFloors()" id="floor-`+buildingNumber+`-`+currentFloor+`-next" >Next</button>
      </div>
  </div>
</div>`);
if(cleaningType=='General Cleaning'){    
  $('#floor-'+buildingNumber+'-'+currentFloor+'-size').children().remove();    
for(var j in generalCleaningSize)
{
  
      $('#floor-'+buildingNumber+'-'+currentFloor+'-size').append('<option value="'+generalCleaningSize[j].name+','+generalCleaningSize[j].cost+'">'+generalCleaningSize[j].name+' ( '+generalCleaningSize[j].min_size+' to '+generalCleaningSize[j].max_size+') - '+generalCleaningSize[j].cost+' KD</option>');

}
}
else{
if(cleaningType=='Deep Cleaning'){      
  $('#floor-'+buildingNumber+'-'+currentFloor+'-size').children().remove();  
  for(var j in deepCleaningSize)
  {
    
        $('#floor-'+buildingNumber+'-'+currentFloor+'-size').append('<option>'+deepCleaningSize[j].name+' ( '+deepCleaningSize[j].min_size+' to '+deepCleaningSize[j].max_size+' )</option>');

  }
  $('.floor-option-'+buildingNumber+'-'+currentFloor).parent().append(`
  <div class="col-md-5 offset-md-1 paint-residue floor-option-`+buildingNumber+`-`+currentFloor+`">
  <div class="m-2">
  <h6 >Paint & Cement Residue ?</h6>
  <div class="form-radio d-flex">
     
      <div class="radio">
        <label>
          <input type="radio" name="floor-`+buildingNumber+`-`+currentFloor+`-residue" value="yes" /><i class="helper"></i>Yes
        </label>
      </div>
      <div class="radio ml-4">
        <label>
          <input type="radio" name="floor-`+buildingNumber+`-`+currentFloor+`-residue" checked="checked" value="no" /><i class="helper"></i>No
        </label>
      </div>
    </div> 
    </div> 
  </div>
  `)
}
else{
  if(cleaningType=='Storage Area'){   
    $('#floor-'+buildingNumber+'-'+currentFloor+'-size').children().remove();     
    for(var j in storageAreaCleaningSize)
    {
     
          $('#floor-'+buildingNumber+'-'+currentFloor+'-size').append('<option>'+storageAreaCleaningSize[j].name+' ( '+storageAreaCleaningSize[j].min_size+' to '+storageAreaCleaningSize[j].max_size+' )</option>');

    }
  }
}
}
}
 }

else{
//  $('.floor-card').hide();
console.log("build no is"+buildingNumber);
var nextBuilding=parseInt(buildingNumber)+1;
$('#tab'+nextBuilding).click();
console.log("clicked");

}

currentFloor=currentFloor+1;
changeLocation();
}
function editFloor(el){
   // $('.floor-card').hide();
   let building_no= $(el).attr('id').split('-')[1];
   let floor_no= $(el).attr('id').split('-')[2];
   $('#floor-'+building_no+'-'+floor_no).show();
   $('#floor-'+building_no+'-'+floor_no+'-next').text('Save Changes');
   $('#floor-'+building_no+'-'+floor_no+'-next').attr('onclick','updateFloor(this)');
}
function updateFloor(el){
   
   
    let building_no= $(el).attr('id').split('-')[1];
    let floor_no= $(el).attr('id').split('-')[2];
    $('#floor-'+building_no+'-'+floor_no).hide();
    $('#result-floor-room-'+building_no+'-'+floor_no).text($('#floor-'+building_no+'-'+floor_no+'-room').val());
    $('#result-floor-size-'+building_no+'-'+floor_no).text($('#floor-'+building_no+'-'+floor_no+'-size').val());
    



}
function deleteFloor(elem){
    let building_no= $(elem).attr('id').split('-')[1];
    let floor_no= $(elem).attr('id').split('-')[2];
   buildingData[building_no-1].floors.splice(floor_no-1, 1);
console.log("building data is "+JSON.stringify(buildingData));
    $('#floor-result-'+building_no+'-'+floor_no).remove();
    for(var i=1;i<=buildingData[building_no-1].floors.length;i++){
        buildingData[building_no-1].floors[i-1].floor=i;
       // $('#result-floor-size-'+building_no+floor_no)
    }

}
function addApartment(elem){
    $('.apartments').children().remove();
    console.log("vhanged apartment");
   // let noOfApartment=$(elem).val();
   
    let building_no= $(elem).attr('name').split('-')[1];
    let floor_no= $(elem).attr('name').split('-')[2];
    let noOfApartment=$('#floor-'+building_no+'-'+floor_no+'-no-of-apartment').val();
    for(var i=1;i<=noOfApartment;i++){
       // app.addSectionFloor('Building'+building_no+'Floor'+floor_no+'Apartment'+i);
       Vue.set(app.serviceSection.sections,'Building'+building_no+'Floor'+floor_no+'Apartment'+i,{keynotes:{},size:'',cost:''});
       Vue.delete(app.serviceSection.sections, 'Building'+building_no+'Floor'+floor_no);

        $('#apartment-'+building_no+'-'+floor_no).append(`
        <hr class="apartment-seperator" id="apartment-seperator-`+building_no+`-`+floor_no+`"></hr>

        <div class="row " >
        <div class="col-md-12 text-center">
            <h6>Apartment `+i+` </h6>
        </div>
       
        <div class="col-md-5  offset-md-1">
        <div class="form-group m-2 ">
        <select id="apartment-`+building_no+`-`+floor_no+`-`+i+`-size" name="apartment-`+building_no+`-`+floor_no+`-`+i+`-size" onchange="setSize(this,'Apartment',`+building_no+`,`+floor_no+`,`+i+`)" >
         
        </select>
        <label for="select" class="control-label">Size</label><i class="bar"></i>
      </div>
           
           
        </div>
        <div class="col-md-5 ">
            <div class="form-group m-2">
                <input type="number" required="required" id="apartment-`+building_no+`-`+floor_no+`-`+i+`-room"/>
                <label for="input" class="control-label" >No of Rooms</label><i class="bar"></i>
              </div>
            
            
        </div>
        <div class="col-md-5 offset-md-1">
        <div class="form-group m-2">
            <input type="number" required="required" id="apartment-`+building_no+`-`+floor_no+`-`+i+`-bathroom"/>
            <label for="input" class="control-label" >No of Bathrooms</label><i class="bar"></i>
          </div>
        
        
    </div>
    <div class="col-md-5 ">
    <div class="form-group m-2">
        <input type="number" required="required" id="apartment-`+building_no+`-`+floor_no+`-`+i+`-window"/>
        <label for="input" class="control-label" >No of Windows</label><i class="bar"></i>
      </div>   
    </div>
    <div class="col-md-5  offset-md-1 mt-2 floor-option-`+buildingNumber+`-`+currentFloor+`">
            
    <div class="form-group m-2 ">
<select required="required" id="apartment-`+buildingNumber+`-`+currentFloor+`-`+i+`-walltype" name="floor-`+buildingNumber+`-`+currentFloor+`-walltype"  onchange="setWallType(this,'Apartment',`+building_no+`,`+floor_no+`,`+i+`)">
<option> Small</option>
<option>Medium</option>
<option>Large</option>

</select>
<label for="select" class="control-label">Wall Type</label><i class="bar"></i>
</div>
 
</div>
<div class="col-md-5   mt-2 floor-option-`+buildingNumber+`-`+currentFloor+`">
            
    <div class="form-group m-2 ">
<select required="required" id="apartment-`+buildingNumber+`-`+currentFloor+`-`+i+`-floortype" name="floor-`+buildingNumber+`-`+currentFloor+`-floortype"  onchange="setFloorType(this,'Apartment',`+building_no+`,`+floor_no+`,`+i+`)">
<option> Small</option>
<option>Medium</option>
<option>Large</option>

</select>
<label for="select" class="control-label">Floor Type</label><i class="bar"></i>
</div>
 
</div>
<div class="col-md-5  mt-2 offset-md-1 floor-option-`+buildingNumber+`-`+currentFloor+`">
  
    <div class="form-group m-2 ">
<select required="required" id="apartment-`+buildingNumber+`-`+currentFloor+`-`+i+`-ceilingtype" name="floor-`+buildingNumber+`-`+currentFloor+`-ceilingtype" onchange="setCeilingType(this,'Apartment',`+building_no+`,`+floor_no+`,`+i+`)" >
<option> Small</option>
<option>Medium</option>
<option>Large</option>

</select>
<label for="select" class="control-label">Ceiling Type</label><i class="bar"></i>
</div>
</div>
<div class="col-md-5  storage-fields  mt-2 floor-option-`+buildingNumber+`-`+currentFloor+`">
  
<div class="form-group m-2  ">
<select required="required" id="apartment-`+buildingNumber+`-`+currentFloor+`-`+i+`-racktype" name="floor-`+buildingNumber+`-`+currentFloor+`-racktype"  >
<option> Wooden</option>
<option>Metal</option>
<option>concrete</option>

</select>
<label for="select" class="control-label">Rack Type</label><i class="bar"></i>
</div>
</div>
<div class="col-md-5 offset-md-1 storage-fields">
    <div class="form-group m-2">
        <input type="number" required="required" id="apartment-`+building_no+`-`+floor_no+`-`+i+`-racks"/>
        <label for="input" class="control-label" >No of Racks</label><i class="bar"></i>
      </div>   
</div>

    <div class="col-md-5  paint-residue ">
    <div class="m-2">
    <h6 >Paint & Cement Residue ?</h6>
    <div class="form-radio d-flex">
       
        <div class="radio">
          <label>
            <input type="radio" name="apartment-`+building_no+`-`+floor_no+`-residue" value="yes" /><i class="helper"></i>Yes
          </label>
        </div>
        <div class="radio ml-4">
          <label>
            <input type="radio" name="apartment-`+building_no+`-`+floor_no+`-residue" checked="checked" value="no" /><i class="helper"></i>No
          </label>
        </div>
      </div> 
      </div> 
    </div>
       
    </div>
        `);
        if(cleaningType=='General Cleaning'){    
          $('#apartment-'+building_no+'-'+floor_no+'-'+i+'-size').children().remove();    
        for(var j in generalCleaningSize)
        {
          
              $('#apartment-'+building_no+'-'+floor_no+'-'+i+'-size').append('<option value="'+generalCleaningSize[j].name+','+generalCleaningSize[j].cost+'">'+generalCleaningSize[j].name+' ( '+generalCleaningSize[j].min_size+' to '+generalCleaningSize[j].max_size+' )</option>');

        }
      }
      else{
        if(cleaningType=='Deep Cleaning'){      
          $('#apartment-'+building_no+'-'+floor_no+'-'+i+'-size').children().remove();  
          for(var j in deepCleaningSize)
          {
            
                $('#apartment-'+building_no+'-'+floor_no+'-'+i+'-size').append('<option>'+deepCleaningSize[j].name+' ( '+deepCleaningSize[j].min_size+' to '+deepCleaningSize[j].max_size+' )</option>');
  
          }
        }
        else{
          if(cleaningType=='Storage Area'){   
            $('#apartment-'+building_no+'-'+floor_no+'-'+i+'-size').children().remove();     
            for(var j in storageAreaCleaningSize)
            {
             
                  $('#apartment-'+building_no+'-'+floor_no+'-'+i+'-size').append('<option>'+storageAreaCleaningSize[j].name+' ( '+storageAreaCleaningSize[j].min_size+' to '+storageAreaCleaningSize[j].max_size+' )</option>');
    
            }
          }
        }
      }
    }
    $('.storage-fields').hide();
    changeLocation();
    if(cleaningType=='Storage Area'){
        $('.storage-fields').show();
        $('.floor-option-'+building_no+'-'+floor_no).hide();
    }
}
function apartmentStat(elem){
    console.log("i ran");
    let building_no= $(elem).attr('name').split('-')[1];
    let floor_no= $(elem).attr('name').split('-')[2];
    $('#apartment-count-'+buildingNumber+'-'+floor_no).show();
    if($(elem).val()=='yes'){
        $('.floor-option-'+building_no+'-'+floor_no).hide();
        $('#no-of-apartment-'+building_no+'-'+floor_no).show();
        $('#apartment-count-'+building_no+'-'+floor_no).show();
        $('#apartment-seperator-'+building_no+'-'+floor_no).show();
      
        $('#apartment-'+building_no+'-'+floor_no).show();
        addApartment(elem);
       /* $('#apartment-'+building_no+'-'+floor_no).append(`
        <hr class="apartment-seperator" id="apartment-seperator-`+buildingNumber+`-`+currentFloor+`"></hr>

        <div class="row " >
        
        <div class="col-md-12 text-center">
            <h6>Apartment 1</h6>
        </div>
       
        <div class="col-md-5  offset-md-1">
        <div class="form-group m-2 ">
        <select id="apartment-`+building_no+`-`+floor_no+`-`+1+`-size" name="apartment-`+building_no+`-`+floor_no+`-`+1+`-size"  >
          <option> Small</option>
          <option>Medium</option>
          <option>Large</option>
        
        </select>
        <label for="select" class="control-label">Size</label><i class="bar"></i>
      </div>
           
        </div>
        <div class="col-md-5 ">
            <div class="form-group m-2">
                <input type="number" required="required" id="apartment-`+building_no+`-`+floor_no+`-room"/>
                <label for="input" class="control-label" >No of Rooms</label><i class="bar"></i>
              </div>
            
            
        </div>
        <div class="col-md-5 offset-md-1">
        <div class="form-group m-2">
            <input type="number" required="required" id="apartment-`+building_no+`-`+floor_no+`-bathroom"/>
            <label for="input" class="control-label" >No of Bathrooms</label><i class="bar"></i>
          </div>
        
        
    </div>
    <div class="col-md-5 ">
    <div class="form-group m-2">
        <input type="number" required="required" id="apartment-`+building_no+`-`+floor_no+`-window"/>
        <label for="input" class="control-label" >No of Windows</label><i class="bar"></i>
      </div>
    
    
</div>
<div class="col-md-5 offset-md-1">
<div class="m-2">
<h6 >Paint & Cement Residue ?</h6>
<div class="form-radio d-flex">
   
    <div class="radio">
      <label>
        <input type="radio" name="apartment-`+buildingNumber+`-`+currentFloor+`-residue" value="yes" onclick="apartmentStat(this)"/><i class="helper"></i>Yes
      </label>
    </div>
    <div class="radio ml-4">
      <label>
        <input type="radio" name="apartment-`+buildingNumber+`-`+currentFloor+`-residue" checked="checked" value="no" onclick="apartmentStat(this)"/><i class="helper"></i>No
      </label>
    </div>
  </div> 
  </div> 
</div>
       
    </div>`);*/
    }
    else{
        $('.floor-option-'+building_no+'-'+floor_no).show();
        $('#apartment-'+building_no+'-'+floor_no).children().remove();
        $('#no-of-apartment-'+building_no+'-'+floor_no).hide();
        $('#apartment-count-'+building_no+'-'+floor_no).hide();

    }
}


function switchTab(el){
   buildingNumber=el;
    console.log('building number is '+buildingNumber);
    currentFloor=buildingData[buildingNumber-1].floors.length+1;
}
 function selectService(elem){
  $('#location-type').val('Location Type');
  $('.building').hide();
  $('.common-field').hide();
  $('.sr-tab-marker').remove();
  $('.tab-panel').remove();
 noOfBuildings=0;
   buildingData=[];
floorCount=0;
currentFloor=1;
buildingNumber=0;
let noOfBuilding = new vanillaSelectBox("#no-of-buildings",{placeHolder: "No of buildings"});
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
    cleaningType=$(elem).find('.service-title').text();
    app.selectServ(cleaningType);
    
    if(cleaningType=='General Cleaning'||cleaningType=='Deep Cleaning'||cleaningType=='Sterilization'){
        $('.item-add-btn').hide();
        $('.building').show();
        $('.common-field').hide();
        $('#field-location-type').show();
        $('#field-no-of-buildings').show();
        $('#field-area-type').show();
        $('.storage-fields').hide();
        $('.items-card').remove();
       
        itemCount=0;
        if(cleaningType=='General Cleaning'){
          getSize('General Cleaning');
          
        }
        else{
          if(cleaningType=='Deep Cleaning'){
            getSize('Deep Cleaning');
          }
          else{
            if(cleaningType=='Sterilization'){
              getSize('Sterilization');
            }
          }
        }
        
    }
    else{
        $('.building').hide();
        $('.common-field').hide();
        $('.sr-tab-marker').remove();
        $('.tab-panel').remove();
       noOfBuildings=0;
         buildingData=[];
    floorCount=0;
    currentFloor=1;
    buildingNumber=0;
    let noOfBuilding = new vanillaSelectBox("#no-of-buildings",{placeHolder: "No of buildings"});
    if(cleaningType=='Facade Cleaning'){
        $('.item-add-btn').remove();
        $('.items-card').remove();
        $('#field-area-type').show();
        itemCount=0;
        addItem('Facade');
       /* $('.item-add-btn').hide();
        $('#field-wall-type').show();
        $('#field-size').show();
        $('#field-hallway-size').show();
        $('#field-location-type').hide();
        $('.storage-fields').hide();
        $('.items-card').remove();
        itemCount=0;*/
        
    }
    else{
        if(cleaningType=='Storage Area'){
           /* $('.item-add-btn').hide();
            $('#field-wall-type').show();
            $('#field-size').show();
            $('#field-hallway-size').hide();
            $('#field-location-type').show();
            $('#field-floor-type').show();
            $('#field-ceiling-type').show();
            $('#field-rack-type').show();
            $('#field-no-of-racks').show();
            $('.items-card').remove();
            upholsteryCount=0;*/
            $('.item-add-btn').hide();
            $('.building').show();
            $('.common-field').hide();
            $('#field-location-type').show();
            $('#field-no-of-buildings').show();
            $('#field-area-type').show();
            $('.storage-fields').show();
            $('.items-card').remove();
            itemCount=0;
            getSize('Storage Area');
        }
        else{
            if(cleaningType=='Car Parking Umbrella'){
               /* $('.item-add-btn').hide();
                $('#field-floor-type').show();
                $('#field-ceiling-type').show();
                $('#field-size').show();
                $('.items-card').remove();
                itemCount=0;*/
                $('#field-area-type').hide();
                $('#field-location-type').hide();
              
                $('.item-add-btn').remove();
                   $('.items-card').remove();
                   itemCount=0;
                   addItem('Umbrella');
            }
            else{
                if(cleaningType=='Outdoor Cleaning'){
                   /* $('.item-add-btn').hide();
                    $('#field-area-type').show();
                    $('#field-size').show();
                    $('.items-card').remove();
                    itemCount=0;*/
                    $('#field-area-type').show();
                    $('#field-location-type').hide();
                  
                    $('.item-add-btn').remove();
                       $('.items-card').remove();
                       itemCount=0;
                       addItem('Outdoor');
                }
                else{
                    if(cleaningType=='Window Cleaning'){
                        $('#field-area-type').show();
                    $('#field-location-type').show();
              
                $('.item-add-btn').remove();
                   $('.items-card').remove();
                   itemCount=0;
                   addItem('Window');
                    }
                    else{
                        if(cleaningType=='Kitchen Cleaning'){
                       /*     $('.item-add-btn').hide();
                            
                            $('#field-floor-type').show();
                            $('#field-wall-type').show();
                            $('#field-ceiling-type').show();
                            $('#field-size').show();
                            $('.items-card').remove();
                            itemCount=0;*/
                         //   $('.item-add-btn').hide();
                         $('#field-area-type').show();
                         $('#field-location-type').show();
                       
                         $('.item-add-btn').remove();
                            $('.items-card').remove();
                            itemCount=0;
                            addItem('Kitchen');


                        }
                        else{
                            if(cleaningType=='Upholstery Cleaning'){
                                $('.items-card').remove();
                                itemCount=0;
                              addItem('Upholstery');
                            
                            }
                            else{
                                if(cleaningType=='Carpet Cleaning'){
                                    $('.items-card').remove();
                                    itemCount=0;
                                    addItem('Carpet');
                                }
                                else{
                                    if(cleaningType=='Mattress Cleaning'){
                                        $('.items-card').remove();
                                        itemCount=0;
                                        addItem('Mattress');
                                    }
                                }
                            }
                            
                        }
                    }
                }
            }
        }
    }

    }
    changeLocation();
    

}
function addItem(item){
    let prev=itemCount;
    itemCount=itemCount+1;
    if(prev==0){
        if(item=='Mattress'||item=='Carpet'||item=='Upholstery')
        {
        $('.item-add-btn').remove();
          $('#field-area-type').show();

          $('#field-area-type').after(`<div class="col-md-12 mt-4 items-card" id="item-`+itemCount+`">
          <i class="fas fa-trash-alt sr-close-btn" onclick="delItem('`+item+`',this)" id="del-1"></i>

             <h6 class="text-center pt-4" id="item-title-`+itemCount+`">`+item+` `+itemCount+`</h6>
              <div class="row mb-4">
              <div class="col-md-12 item-cleaningtype">
              <div class="form-radio d-flex mt-4 mx-auto">

              <div class="radio">
                <label>
                  <input type="radio" name="item-cleaning-`+itemCount+`" value="vaccum"  id="item-material-`+itemCount+`"/><i class="helper"></i>Vaccum Cleaning
                </label>
              </div>
              <div class="radio ml-4">
                <label>
                  <input type="radio" name="item-cleaning-`+itemCount+`" checked="checked" value="deep"/><i class="helper"></i>Deep Cleaning
                </label>
              </div>
            </div>
              </div>
              <div class="col-md-6 mt-4 " id="item-age-`+itemCount+`">
              <input type="number" placeholder="Age  (Months) " id="item-`+itemCount+`-age"  name="item-`+itemCount+`-age" class="sr-input"/>
             
              </div>
              <div class="col-md-6 mt-4">
              <select id="item-`+itemCount+`-material" multiple  name="item-`+itemCount+`-material">
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            
         </select>
              </div>
              <div class="col-md-6 mt-4 ">
              <select id="item-`+itemCount+`-color"  name="item-`+itemCount+`-color">
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
            
         </select>
              </div>
              <div class="col-md-6 mt-4">
              <select id="item-`+itemCount+`-size"  name="item-`+itemCount+`-size">
              <option value="small">small</option>
              <option value="medium">medium</option>
              <option value="large">large</option>
              
            
         </select>
              </div>
              <div class="col-md-6 ">
              <div class="form-radio d-flex mt-4 ">
                Any Stain ?<br>
              <div class="radio ml-4" onclick="showReason(`+itemCount+`)">
                <label>
                  <input type="radio" name="item-stain-`+itemCount+`" value="vaccum"  id="item-material-`+itemCount+`"  /><i class="helper"></i>Yes
                </label>
              </div>
              <div class="radio ml-4" onclick="hideReason(`+itemCount+`)">
                <label>
                  <input type="radio" name="item-stain-`+itemCount+`" checked="checked" value="deep" /><i class="helper"></i>No
                </label>
              </div>
            </div>
              </div>
              <div class="col-md-6 mt-4 stain-reason" id="item-reason-`+itemCount+`">
              <select id="item-`+itemCount+`-type"  name="item-`+itemCount+`-type" multiple>
              <option value="small">small</option>
              <option value="medium">medium</option>
              <option value="large">large</option>
              
            
         </select>
              </div>
              <div class="col-md-6 mt-4 stain-reason" id="item-stain-age-`+itemCount+`">
              <input type="number" placeholder="Age of Stain (Weeks) " id="item-`+itemCount+`-stain-age"  name="item-`+itemCount+`-stain-age" class="sr-input"/>
             
              </div>

              </div>
          </div>
          <div class="item-add-btn" onclick="addItem('`+item+`')" id="item-btn-`+itemCount+`">
          <i class="fa fa-plus-circle" aria-hidden="true"></i>

          </div>
          `);

          $('.item-add-btn').show();
         
          materialSelectBox[itemCount]= new vanillaSelectBox("#item-"+itemCount+"-material",{placeHolder: "Material"});
          colorSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-color",{placeHolder: "Color"});
          sizeSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-size",{placeHolder: "Size"});
          reasonSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-type",{placeHolder: "Stain Type"});
        }
        else{
            if(item=='Kitchen'||item=='Facade'||item=='Umbrella'||item=='Window'||item=='Outdoor'){
                $('#field-location-type').after(`<div class="col-md-12 mt-4 items-card" id="item-`+itemCount+`">
                <i class="fas fa-trash-alt sr-close-btn" onclick="delItem('`+item+`',this)" id="del-1"></i>
      
                   <h6 class="text-center pt-4" id="item-title-`+itemCount+`">`+item+` `+itemCount+`</h6>
                    <div class="row mb-4">
                    <div class="col-md-12 item-cleaningtype">
                    <div class="form-radio d-flex mt-4 mx-auto">
      
                    <div class="radio">
                      <label>
                        <input type="radio" name="item-condition-`+itemCount+`" value="used"  id="item-condition-`+itemCount+`"/><i class="helper"></i>Used
                      </label>
                    </div>
                    <div class="radio ml-4">
                      <label>
                        <input type="radio" name="item-condition-`+itemCount+`" checked="checked" value="new"/><i class="helper"></i>New
                      </label>
                    </div>
                  </div>
                    </div>
                    <div class="col-md-6 mt-4 " id="item-age-`+itemCount+`">
                    <input type="number" placeholder="Age  (Months) " id="item-`+itemCount+`-age"  name="item-`+itemCount+`-age" class="sr-input"/>
                   
                    </div>
                    <div class="col-md-6 mt-4">
                    <select id="item-`+itemCount+`-size"  name="item-`+itemCount+`-size">
                    <option value="1">Small</option>
                    <option value="2">Medium</option>
                    <option value="3">Large</option>
                   
                  
               </select>
               </div>
                    <div class="col-md-6 mt-4">
                    <select id="item-`+itemCount+`-floor" multiple  name="item-`+itemCount+`-floor">
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                  
               </select>
                    </div>
                    <div class="col-md-6 mt-4 ">
                    <select id="item-`+itemCount+`-wall"  name="item-`+itemCount+`-wall">
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                  
               </select>
                    </div>
                    <div class="col-md-6 mt-4">
                    <select id="item-`+itemCount+`-ceiling"  name="item-`+itemCount+`-ceiling">
                    <option value="small">small</option>
                    <option value="medium">medium</option>
                    <option value="large">large</option>
                    
                  
               </select>
                    </div>
                    <div class="col-md-6 oil-residue">
                    <div class="form-radio d-flex mt-4 ">
                      Oil Residue ?<br>
                    <div class="radio ml-4" >
                      <label>
                        <input type="radio" name="item-oil-residue-`+itemCount+`" value="vaccum"  id="item-oil-residue-`+itemCount+`"  /><i class="helper"></i>Yes
                      </label>
                    </div>
                    <div class="radio ml-4" >
                      <label>
                        <input type="radio" name="item-oil-residue-`+itemCount+`" checked="checked" value="deep" /><i class="helper"></i>No
                      </label>
                    </div>
                  </div>
                    </div>
                   
                    
      
                    </div>
                </div>
                <div class="item-add-btn" onclick="addItem('`+item+`')" id="item-btn-`+itemCount+`">
                <i class="fa fa-plus-circle" aria-hidden="true"></i>
      
                </div>
                `);
               
      
                $('.item-add-btn').show();
                floorSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-floor",{placeHolder: "Floor type"});
                wallSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-wall",{placeHolder: "Wall Type"});
                sizeSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-size",{placeHolder: "Size"});
                 ceilingSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-ceiling",{placeHolder: "Ceiling Type"});
                 if(item=='Facade'){
                    $('#item-'+itemCount+'-floor').parent().remove();
                    $('#item-'+itemCount+'-ceiling').parent().remove();
                    // $('#item-'+itemCount+'-ceiling').parent().remove();
                     $('.item-cleaningtype').remove();
                     $('.oil-residue').remove();
                    $('#item-age-'+itemCount).replaceWith(`
                    <div class="col-md-6 mt-4">
                    <select id="item-`+itemCount+`-hallway-size"  name="item-`+itemCount+`-hallway-size">
                         <option value="1">Small</option>
                         <option value="2">Medium</option>
                         <option value="3">Large</option>    
                     </select>
                     </div>
                    `);
                    hallwaySelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-hallway-size",{placeHolder: "Hallway Size"});
                }
                else{
                    if(item=='Umbrella'){
                        $('#item-'+itemCount+'-wall').parent().remove();
                        $('.item-cleaningtype').remove();
                     $('.oil-residue').remove();
                     $('#item-age-'+itemCount).remove();
                    }
                    else{
                        if(item=='Window'){
                            $('.item-cleaningtype').remove();
                            $('#item-'+itemCount+'-floor').parent().remove();
                            $('#item-'+itemCount+'-ceiling').parent().remove();
                            $('#item-'+itemCount+'-wall').parent().remove();
                            $('#item-'+itemCount+'-size').parent().parent().append(`
                            <div class="col-md-6 mt-4 ">
                            <select id="item-`+itemCount+`-sides"  name="item-`+itemCount+`-sides">
                            <option value="1">Outside & Inside</option>
                            <option value="2">Outside</option>
                            <option value="3">Inside</option>
                            </select>
                            </div>
                            `);
                             $('.oil-residue').remove();
                             $('#item-age-'+itemCount).remove();
                             sidesSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-sides",{placeHolder: "Sides"});
                        }
                        else{
                            if(item=='Outdoor'){
                                $('.item-cleaningtype').remove();
                                $('#item-'+itemCount+'-floor').parent().remove();
                                 $('#item-'+itemCount+'-ceiling').parent().remove();
                                $('#item-'+itemCount+'-wall').parent().remove();
                                $('.oil-residue').remove();
                             $('#item-age-'+itemCount).remove();
                            }
                        }
                    }
                }
                
            }
        }
          
 }
  else{
    if(item=='Mattress'||item=='Carpet'||item=='Upholstery')
    {
    $('#item-btn-'+prev).after(`<div class="col-md-12 mt-4 items-card" id="item-`+itemCount+`">
    <i class="fas fa-trash-alt sr-close-btn" onclick="delItem('`+item+`',this)"></i>
    
       <h6 class="text-center pt-4" id="item-title-`+itemCount+`">`+item+` `+itemCount+`</h6>
      
              <div class="row mb-4">
        <div class="col-md-12 item-cleaningtype">
        <div class="form-radio d-flex mt-4 ">

        <div class="radio">
          <label>
            <input type="radio" name="item-cleaning-`+itemCount+`" value="vaccum"  id="item-cleaning-`+itemCount+`"/><i class="helper"></i>Vaccum Cleaning
          </label>
        </div>
        <div class="radio ml-4">
          <label>
            <input type="radio" name="item-cleaning-`+itemCount+`" checked="checked" value="deep"/><i class="helper"></i>Deep Cleaning
          </label>
        </div>
      </div>
        </div>
        <div class="col-md-6 mt-4 " id="item-age-`+itemCount+`">
        <input type="number" placeholder="Age  (Months) " id="item-`+itemCount+`-age"  name="item-`+itemCount+`-age" class="sr-input"/>
       
        </div>
        <div class="col-md-6 mt-4">
        <select id="item-`+itemCount+`-material" multiple  name="item-`+itemCount+`-material">
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
      
   </select>
        </div>
        <div class="col-md-6 mt-4">
        <select id="item-`+itemCount+`-color"  name="item-`+itemCount+`-color" >
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
      
   </select>
        </div>
        <div class="col-md-6 mt-4" >
        <select id="item-`+itemCount+`-size"  name="item-`+itemCount+`-size">
        <option value="small">small</option>
        <option value="medium">medium</option>
        <option value="large">large</option>
        
      
   </select>
        </div>
        <div class="col-md-6 ">
        <div class="form-radio d-flex mt-4 ">
          Any Stain ?<br>
        <div class="radio ml-4" onclick="showReason(`+itemCount+`)">
          <label>
            <input type="radio" name="item-stain-`+itemCount+`" value="vaccum"  id="item-material-`+itemCount+`"  /><i class="helper"></i>Yes
          </label>
        </div>
        <div class="radio ml-4" onclick="hideReason(`+itemCount+`)">
          <label>
            <input type="radio" name="item-stain-`+itemCount+`" checked="checked" value="deep" /><i class="helper"></i>No
          </label>
        </div>
      </div>
        </div>
        <div class="col-md-6 mt-4 stain-reason" id="item-reason-`+itemCount+`">
        <select id="item-`+itemCount+`-type"  name="item-`+itemCount+`-type" multiple>
        <option value="small">small</option>
        <option value="medium">medium</option>
        <option value="large">large</option>
        
      
   </select>
        </div>
        <div class="col-md-6 mt-4 stain-reason" id="item-stain-age-`+itemCount+`">
        <input type="number" placeholder="Age of Stain (Weeks) " id="item-`+itemCount+`-stain-age"  name="item-`+itemCount+`-stain-age" class="sr-input"/>
       
        </div>
        </div>
    </div>
    <div class="item-add-btn" onclick="addItem('`+item+`')" id="item-btn-`+itemCount+`">
    <i class="fa fa-plus-circle" aria-hidden="true"></i>

    </div>
    `);
    $('.item-add-btn').show();
    $('#item-btn-'+prev).remove();
    
    materialSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-material",{placeHolder: "Material"});
    colorSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-color",{placeHolder: "Color"});
    sizeSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-size",{placeHolder: "Size"});
    reasonSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-type",{placeHolder: "Stain Type"});
    /* $("#item-"+prev+'-material').show();
     $("#item-"+prev+'-color').show();
     $("#item-"+prev+'-size').show();*/
    }
    else{
        if(item=='Kitchen'||item=='Facade'||item=='Window'||item=='Umbrella'||item=='Outdoor'){
            $('#item-btn-'+prev).after(`<div class="col-md-12 mt-4 items-card" id="item-`+itemCount+`">
            <i class="fas fa-trash-alt sr-close-btn" onclick="delItem('`+item+`',this)" id="del-1"></i>
  
               <h6 class="text-center pt-4" id="item-title-`+itemCount+`">`+item+` `+itemCount+`</h6>
                <div class="row mb-4">
                <div class="col-md-12 item-cleaningtype">
                <div class="form-radio d-flex mt-4 mx-auto">
  
                <div class="radio">
                  <label>
                    <input type="radio" name="item-condition-`+itemCount+`" value="used"  id="item-material-`+itemCount+`"/><i class="helper"></i>Used
                  </label>
                </div>
                <div class="radio ml-4">
                  <label>
                    <input type="radio" name="item-condition-`+itemCount+`" checked="checked" value="new"/><i class="helper"></i>New
                  </label>
                </div>
              </div>
                </div>
                <div class="col-md-6 mt-4 " id="item-age-`+itemCount+`">
                <input type="number" placeholder="Age  (Months) " id="item-`+itemCount+`-age"  name="item-`+itemCount+`-age" class="sr-input"/>
               
                </div>
                <div class="col-md-6 mt-4">
                <select id="item-`+itemCount+`-size"  name="item-`+itemCount+`-size">
                <option value="1">Small</option>
                <option value="2">Medium</option>
                <option value="3">Large</option>    
           </select>
           </div>
                <div class="col-md-6 mt-4">
                <select id="item-`+itemCount+`-floor" multiple  name="item-`+itemCount+`-floor">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
              
           </select>
                </div>
                <div class="col-md-6 mt-4 ">
                <select id="item-`+itemCount+`-wall"  name="item-`+itemCount+`-wall">
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
              
           </select>
                </div>
                <div class="col-md-6 mt-4">
                <select id="item-`+itemCount+`-ceiling"  name="item-`+itemCount+`-ceiling">
                <option value="small">small</option>
                <option value="medium">medium</option>
                <option value="large">large</option>
                
              
           </select>
                </div>
                <div class="col-md-6 oil-residue">
                <div class="form-radio d-flex mt-4 ">
                  Oil Residue ?<br>
                <div class="radio ml-4" >
                  <label>
                    <input type="radio" name="item-stain-`+itemCount+`" value="vaccum"  id="item-material-`+itemCount+`"  /><i class="helper"></i>Yes
                  </label>
                </div>
                <div class="radio ml-4" >
                  <label>
                    <input type="radio" name="item-stain-`+itemCount+`" checked="checked" value="deep" /><i class="helper"></i>No
                  </label>
                </div>
              </div>
                </div>
            
  
                </div>
            </div>
            <div class="item-add-btn" onclick="addItem('`+item+`')" id="item-btn-`+itemCount+`">
            <i class="fa fa-plus-circle" aria-hidden="true"></i>
  
            </div>
            `);
  
            $('.item-add-btn').show();
            $('#item-btn-'+prev).remove();
            floorSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-floor",{placeHolder: "Floor type"});
            wallSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-wall",{placeHolder: "Wall Type"});
            sizeSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-size",{placeHolder: "Size"});
             ceilingSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-ceiling",{placeHolder: "Ceiling Type"});
             $('.item-cleaningtype').remove();
             if(item=='Facade'){
                $('#item-'+itemCount+'-floor').parent().remove();
                $('#item-'+itemCount+'-ceiling').parent().remove();
                $('#item-age-'+itemCount).replaceWith(`
                <div class="col-md-6 mt-4">
                <select id="item-`+itemCount+`-hallway-size"  name="item-`+itemCount+`-hallway-size">
                     <option value="1">Small</option>
                     <option value="2">Medium</option>
                     <option value="3">Large</option>    
                 </select>
                 </div>
                `);
                $('.oil-residue').remove();
                hallwaySelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-hallway-size",{placeHolder: "Hallway Size"});
            }
            else{
                if(item=='Umbrella'){
                    $('#item-'+itemCount+'-wall').parent().remove();
                    $('.item-cleaningtype').remove();
                 $('.oil-residue').remove();
                 $('#item-age-'+itemCount).remove();
                }
                else{
                    if(item=='Window'){
                        $('.item-cleaningtype').remove();
                        $('#item-'+itemCount+'-floor').parent().remove();
                        $('#item-'+itemCount+'-ceiling').parent().remove();
                        $('#item-'+itemCount+'-wall').parent().remove();
                        $('#item-'+itemCount+'-size').parent().parent().append(`
                        <div class="col-md-6 mt-4 ">
                        <select id="item-`+itemCount+`-sides"  name="item-`+itemCount+`-sides">
                        <option value="1">Outside & Inside</option>
                        <option value="2">Outside</option>
                        <option value="3">Inside</option>
                        </select>
                        </div>
                        `);
                         $('.oil-residue').remove();
                         $('#item-age-'+itemCount).remove();
                         sidesSelectBox[itemCount]=new vanillaSelectBox("#item-"+itemCount+"-sides",{placeHolder: "Sides"});
                    }
                    else{
                        if(item=='Outdoor'){
                            $('.item-cleaningtype').remove();
                            $('#item-'+itemCount+'-floor').parent().remove();
                             $('#item-'+itemCount+'-ceiling').parent().remove();
                            $('#item-'+itemCount+'-wall').parent().remove();
                            $('.oil-residue').remove();
                         $('#item-age-'+itemCount).remove();
                        }
                    }
                }
            }
        }

  }
}
  if(cleaningType=='Mattress Cleaning'){
        $('.item-cleaningtype').hide();
  }
 
  

}
function delItem(item,elem){
    calcVal();
    
    $(elem).parent().remove();
    let currentId=parseInt($(elem).parent().attr('id').split('-')[1]);
    
    console.log("current id is "+currentId);
  if(currentId<itemCount){
      for(var j=currentId+1;j<=itemCount;j++){
        $('#item-'+j).attr('id','#item-'+(j-1));
        $('#item-'+j+'-color').attr({'id':'item-'+(j-1)+'-color','name':'item-'+(j-1)+'-color'});
        $('#item-'+j+'-material').attr({'id':'item-'+(j-1)+'-material','name':'item-'+(j-1)+'-material'});
        $('#item-'+j+'-size').attr({'id':'item-'+(j-1)+'-size','name':'item-'+(j-1)+'-size'});
        $('#item-btn-'+j).attr({'id':'item-btn-'+(j-1)});

        $('[name=item-cleaning-'+j+']').attr({'name':'item-cleaning-'+(j-1)});
        $('#item-title-'+j).text(item + ' '+(j-1));
      }
  }
    itemCount=itemCount-1;
    items.splice(currentId-1,1);
}
function calcVal(){
    for(var i=1;i<=itemCount;i++){
        items.push({
            'material':$('#item-'+i+"-material").val(),
            'color':$('#item-'+i+"-color").val(),
            'Cleaning':$('input[name=item-cleaning-'+i+']:checked').val(),
            'size':$('#item-'+i+"-size").val(),
        });
    }
    console.log("added els are "+JSON.stringify(items));
}
function changeLocation(){

    location_type=$('#location-type').val();
    if(cleaningType=='Deep Cleaning' && location_type=='Post Construction'){
       
        $('.paint-residue').show();
    }
    else{
        $('.paint-residue').hide();
    }
}


function mapData(){
    console.log("service data is"+ JSON.stringify(serviceData));
    sectionData.service_type=cleaningType;
    sectionData.location_type=location_type;
    sectionData.area_type=$('#area-type').val();
    sectionData.area_type=serviceData.area_type; 
    for(var i=0;i<serviceData.building.length;i++){
        for(var j=0;j<serviceData.building[i].floors.length;j++){
            if(serviceData.building[i].floors[j].apartments.length>0){
                for(var k=0;k<serviceData.building[i].floors[j].apartments.length;k++)
                {
                    sectionData.sections['Building'+i+'Floor'+j+'Apartment'+k]={size:''};
                    sectionData.sections['Building'+i+'Floor'+j+'Apartment'+k].size=serviceData.building[i].floors[j].apartments[k].size;
                  //  sectionData.size=serviceData.building[i].floors[j].apartments[k].size;
                  console.log("i ran")
                }
            }
            else{
                sectionData.sections['Building'+i+'Floor'+j]={size:{}};
                sectionData.sections['Building'+i+'Floor'+j].size=serviceData.building[i].floors[j].size;
               // sectionData.size=serviceData.building[i].floors[j].size;
               console.log("i ran")
            }
        }
    }
    console.log("mapped data is "+JSON.stringify(sectionData));
}

$('input[type=radio][name=bedStatus]').change(function() {
    if (this.value == 'allot') {
        alert("Allot Thai Gayo Bhai");
    }
    else if (this.value == 'transfer') {
        alert("Transfer Thai Gayo");
    }
});
function showReason(itemid){

    $('#item-reason-'+itemid).show();
    $('#item-stain-age-'+itemid).show();

}
function hideReason(itemid){
    $('#item-reason-'+itemid).hide();
    $('#item-stain-age-'+itemid).hide();
}

function getSize(srvc){
  axios.get('/customer/ajax/getservicesizeprice?service_type='+srvc)
  .then(function (response) {
    console.log(response);
    if(srvc=='General Cleaning'){
      generalCleaningSize=response.data;
      console.log("general clenainhg sise is "+JSON.stringify(generalCleaningSize));
    }
   
    else{
      if(srvc=='Deep Cleaning'){
        deepCleaningSize=response.data;
        console.log("deep clenainhg sise is "+JSON.stringify(deepCleaningSize));
      }
      else{
        if(srvc=='Storage Area'){
          storageAreaCleaningSize=response.data;
          console.log("storage clenainhg sise is "+JSON.stringify(storageAreaCleaningSize));
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
function setSize(elem,type,building,floor,apartment){
  console.log("size is "+$(elem).val());
  if(type=='Floor'){
    Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor],"size",$(elem).val().split(',')[0]);
    Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor],"cost",$(elem).val().split(',')[1]);
    app.findCost();
 

    
    
  
  }
  if(type=='Apartment'){
   delete app.serviceSection.sections['Building'+building+'Floor'+floor];
   Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor+'Apartment'+apartment],"size",$(elem).val().split(',')[0]);
   Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor+'Apartment'+apartment],"cost",$(elem).val().split(',')[1]);
    app.findCost();
  
} 
}
function setWallType(elem,type,building,floor,apartment){
    console.log("size is "+$(elem).val());
    if(type=='Floor'){
        Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor].keynotes,'wall_type',$(elem).val());
         
   
  
      
      
    
    }
    if(type=='Apartment'){
     delete app.serviceSection.sections['Building'+building+'Floor'+floor];
     Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor+'Apartment'+apartment].keynotes,'wall_type',$(elem).val());
      
  } 
  }
  function setFloorType(elem,type,building,floor,apartment){
    console.log("floor is "+$(elem).val());
    if(type=='Floor'){
      Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor].keynotes,'floor_type',$(elem).val());
          
    }
    if(type=='Apartment'){
     delete app.serviceSection.sections['Building'+building+'Floor'+floor];
     Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor]+'Apartment'+apartment.keynotes,'floor_type',$(elem).val());
     
     
    
  } 
  }
  function setCeilingType(elem,type,building,floor,apartment){
    console.log("size is "+$(elem).val());
    if(type=='Floor'){
        Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor].keynotes,'ceiling_type',$(elem).val());
        
   
  
      
      
    
    }
    if(type=='Apartment'){
     delete app.serviceSection.sections['Building'+building+'Floor'+floor];
     
     Vue.set(app.serviceSection.sections['Building'+building+'Floor'+floor+'Apartment'+apartment].keynotes,'ceiling_type',$(elem).val());
      
    
  } 
  }
  function selectDuration(duration){
      console.log("duration is "+duration);
      app.selectedDuration=duration;
  }

function splitCamelCaseToString(s) {
    return s.split(/(?=[A-Z])/).join(' ');
}