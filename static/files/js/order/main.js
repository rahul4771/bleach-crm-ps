

$(document).ready(function () {
 /* $("#content-slider").lightSlider({

          item:2,
          loop:true,
          slideMove:1,
          speed:600,
         
  });*/
  console.log("moment date is "+ moment().format('MM/DD/YYYY'))
  $('#calendar').datepicker({
    language: "en",
    startDate:moment().format('MM/DD/YYYY')
    
  });
  
  $('#calendar').on('changeDate', function() {
    $('#date_hidden').val(
        $('#calendar').datepicker('getFormattedDate')
    );
   // console.log("moment is")
    console.log($('#date_hidden').val()) 
    var date=$('#date_hidden').val()
    var day=date.split('/')[1]
    var month=date.split('/')[0]
    var year=date.split('/')[2]
    var newdate=day+'-'+month+'-'+year
    app.selected_date=newdate
    //console.log($('#date_hidden').val().replace(/\//g, '-'))
    app.setDate($('#date_hidden').val())
    this.selected_cleaning_date=moment(date,'MM/DD/YYYY').format('DD-MM-YYYY')
    app.getSlotes(moment(date,'MM/DD/YYYY').format('DD-MM-YYYY'))
   
    app.getVisitSlotes(moment(date,'MM/DD/YYYY').format('DD-MM-YYYY'))
});

  $(".owl-carousel").owlCarousel({
    items: 2,
    nav: true,
    margin: 10,
    navText: [
      `<i class='fa fa-chevron-left service-control' @click='prevService()'></i>`,
      `<i class='fa fa-chevron-right service-control'></i>`,
    ],
  });
   app.paymentType = $( "#id_payment" ).val()
  app.amount = $("#id_amount").text()

});




function myFunction(book_id) {
  document.getElementById("visti-section"+book_id+"").classList.toggle("not-show");
  document.getElementById("myDropdown"+book_id+"").classList.toggle("show");
}
function onClick(element) {
  document.getElementById("img01").src = element.src;
  document.getElementById("modal01").style.display = "block";
}
function onClose() {
  
  document.getElementById("modal01").style.display = "none";
}
/*function editSection(section){
  console.log("i m here")
  var sectiondata=$(section).data()
  console.log("section is "+JSON.stringify(sectiondata))
  app.sectionData=sectiondata
  $('#edit-dialog-tigger').click()
  app.editSectionData.section_cost=sectiondata.section_cost
  app.editSectionData.section_name=sectiondata.section_name
  
}*/
function editSection(service){
  
  
  var index=$(service).data('index')
  var sid=$(service).data('section_id')
  var eval_book_id=$(service).data('eval_book_id')
  app.action_type="Edit"

  app.service_type=$(service).data('service')
  app.getProductivity()
  console.log("index is"+index)
 // var sectiondata=$(section).data()
 app.getSection(eval_book_id)
 app.editSectionData.section_id=sid
if(app.service_type=='Kitchen Cleaning'){
  app.editSectionData.new_kitchen=app.sections[index-1].new_kitchen
  app.editSectionData.oil_residue=app.sections[index-1].oil_residue
}
if(app.service_type=='Facade Cleaning'){
  app.editSectionData.is_highprice_facade=app.sections[index-1].is_highprice_facade
  
}
 app.editSectionData.keynotes=app.sections[index-1].keynotesections
  console.log("section is "+JSON.stringify(app.sections[index-1]))
  app.sectionData=app.sections[index-1]
  app.editSectionData.size=app.sections[index-1].size
  app.editSectionData.size['combined_size']=app.sections[index-1].size.name+' ('+app.sections[index-1].size.min_size+' sq.m - '+app.sections[index-1].size.max_size+' sq.m )'
  if(app.sections[index-1].upholstery_type){
    app.editSectionData.upholstery_type=app.sections[index-1].upholstery_type
  }
  app.getOtherKeynotes()
      app.getTheKitchens()
     
      app.recalcKeynoteCost()
  $('#edit-dialog-tigger').click()
  app.editSectionData.section_cost=app.sectionData.section_cost
  app.editSectionData.section_name=app.sectionData.section_name
  app.removeInitialKitchenCost()
  if(app.sectionData.wall_type!="" && app.sectionData.wall_type!=null)
  {
    app.editSectionData.wall_type=app.sectionData.wall_type.split(',')
  }
  if(app.sectionData.floor_type!="" && app.sectionData.floor_type!=null)
  {
    app.editSectionData.floor_type=app.sectionData.floor_type.split(',')
  }
  if(app.sectionData.ceiling_type!="" && app.sectionData.ceiling_type!=null)
  {
    app.editSectionData.ceiling_type=app.sectionData.ceiling_type.split(',')
  }
  if(app.sectionData.materials!="" && app.sectionData.materials!=null )
  {
    app.editSectionData.materials=app.sectionData.materials.split(',')
  }
  
  
  
  
  //app.findSize()
  
}

function editService(service){
  app.service_type=$(service).data('service')
  app.edit=true
  app.getProductivity()
  
}
function openPaymentEdit(payment){
 var paymentDetails=$(payment).data()
 app.paymentData.payment_method=paymentDetails.payment_method
 app.paymentData.total_amount=paymentDetails.total_amount
 app.paymentData.final_amount=paymentDetails.final_amount
 app.total_amount=paymentDetails.total_amount
 app.paymentData.discount=paymentDetails.discount
 app.paymentData.amount_before_cleaning=paymentDetails.amount_before_cleaning
 app.paymentData.amount_after_cleaning=paymentDetails.amount_after_cleaning
 app.openPayment()
}
function openCleaningDate(service){
  app.cleaning_action='add_cleaning'
  $('#cleaning-date-tigger').click()
  var data=$(service).data()
  app.no_of_cleaners=data.no_of_cleaners
  console.log("cleaners:"+data.no_of_cleaners)
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  
  app.getSlotes(moment().format('DD-MM-YYYY'))
  $("#calendar").datepicker("update", (moment().format('MM/DD/YYYY')));
}
function editCleaningDate(service){
  app.cleaning_action='edit_cleaning'
  $('#cleaning-date-tigger').click()
  var data=$(service).data()
  app.no_of_cleaners=data.no_of_cleaners
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  app.schedule_id=data.id
  
  app.cleaning_start_date=data.cleaning_start_date
  app.selected_cleaning_date=data.cleaning_start_date
  app.getSlotes(app.cleaning_start_date)
  $('#date_hidden').val((moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY')))
  $("#calendar").datepicker("update", moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY'));
  app.setDate(moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY'))
  
}
function deleteCleaningDate(service){
  app.cleaning_action='cancell_cleaning'
  app.reduction_status=false
  console.log("inside del cleaning")
  $('#cleaning-delete-tigger').click()
  var data=$(service).data()
  app.no_of_cleaners=data.no_of_cleaners
  app.cleaning_policy='ONE TIME SERVICE'
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  app.schedule_id=data.id
  
  app.cleaning_start_date=data.cleaning_start_date
  app.selected_cleaning_date=data.cleaning_start_date
 
}
function cancelCleaningDate(service){
 
  app.cleaning_action='cancell_cleaning'
  app.reduction_status=false
  $('#cleaning-cancel-tigger').click()
  var data=$(service).data()
  
  app.no_of_cleaners=data.no_of_cleaners
  app.cleaning_policy='SUBSCRIPTION'
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  app.schedule_id=data.id
  app.reducing_total=parseInt(data.estimated_cost)
  app.cleaning_start_date=data.cleaning_start_date
  app.selected_cleaning_date=data.cleaning_start_date
 
}
function addSection(service){
  app.service_type=$(service).data('service')
  app.editSectionData=
    {
      "section_name":"",
      "size":"",
      "wall_type":[],
      "ceiling_type":[],
      "floor_type":[],
      "cement_residue":false,
      "section_cost":"",
      "section_net_cost":"",
      "keynotes":[],
      "new_kitchen":false,
     "is_highprice_facade":false,
     "is_highprice_window":false,
  }
 app.kitchen_keynotes=[]
 app.other_keynotes=[]
  app.action_type="Add"
  app.getProductivity()
  $('#edit-dialog-tigger').click()
}
const app = new Vue({
  el: "#app",
  
  delimiters: ["<%", "%>"],
  
  mounted() {
    this.getOrderId()
    this.setDate(moment().format('MM/DD/YYYY'))
    this.selected_date=moment().format('DD-MM-YYYY')
    $('#date_hidden').val(moment().format('MM/DD/YYYY'))
    this.getTheSize('Kitchen Cleaning')
    console.log("service is"+$('.service-name'))
    var service=$('.service-name')
    var book_ids=$('.service_id')
    console.log("book ids ae"+JSON.stringify(book_ids))
    for(var i=0;i<service.length;i++)
    {
      this.services.push({
        id:$(book_ids[i]).val(),
        name:$(service[i]).text()})
    }
    
   
    
  },
  components: { Multiselect: window.VueMultiselect.default },

  data: {
    all_val:false,
    reduction_status:false,
    no_of_visits:0,
    services:[],
    reducing_total:0,
    selected_cleaning_date:'',
    cleaning_policy:'',
    highprice_facade:[],
    lowprice_facade:[],
    highprice_window:[],
    lowprice_window:[],
    fixed_section_cost:null,
    soltdate: null, 
    edit: false,
    cancelDialog:false,
    editSectionDialog:false,
    year:null,
    day:null,
    month:null,
    paymentType:"",
    key: "",
    breakDownFlag:false,
    amount:"",
    contacts:[],
    sectionData:{},
    value: [],
    floor_type:'',
    wall_type:'',
    ceiling_type:'',
    service_type:'',
    currentServiceType:'',
    service_productivity:[],
    selected_size:{},
    walltypes:["BRICKS","GLASS","CONCRETE","CERAMIC","GYPSUM","FABRIC","RUBBER","STONE","TERRAZO","STAINLESS","VINYL","WOODEN","OTHERS"],
  ceilingtypes:["WOODEN","GLASS","CONCRETE","CERAMIC","GYPSUM","FOAM","PLASTIC","FABRIC","RUBBER","STAINLESS","VENYL","OTHERS"],
  floortypes:["MARBLE","GLASS","STONE","CERAMIC","CONCRETE","BRICKS","WOODEN","TERRAZO","OTHERS"],
  materials:["POLYESTER","NATURAL FIBER","SYNTHETIC","LEATHER","OLEFIN","POLYPROPYLENE","NYLON"],
  colors:["GREEN","SILVER","VIOLET","WHITE","BLACK","BEIGE","BLUE","GREY","RED","CREAM","MULTI","OFF WHITE","MEROON","ORANGE","PINK","GOLD","BROWN","YELLOW","ROYAL BLUE","LILAC","OTHERS"],
    
             productivity:{},
             editSectionData:{
              size:{},
             keynotes:[],
              section_cost:0,
              section_name:'',
              floor_type:[],
              ceiling_type:[],
              wall_type:[],
              material:[],
              category:'Floor',
              age:null,
              new_kitchen:false
             },
             section_cost:0,
             orderId:'',
             sections:[],
             currentSection:[],
             gotSection:false,
           
             eval_book_id:'',
             action_type:'',
             paymentData:{
               discount:'',
               amount_before_cleaning:'',
               amount_after_cleaning:'',
               amount:'',
               payment_method:''
             },
             total_amount:0,
             deleteSectionData:{
               section_id:''
             },
             no_of_cleaners:0,
             schedule_serviceTypes:[],
             timeSlots:{},
             selectedSlots:[],
             cleaning_hours:null,
             no_of_cleaners:null,
             no_of_slots:0,
             selected_date:'',
             evaluation_book_id:'',
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
            parsedTimeSlots:[],
            selected_no_of_cleaners:null,
            visit_err:'',
            cleaning_action:'',
            cleaning_start_date:'',
            schedule_id:'',
            newkeynote:{
              sub_area:'',
              quantity:''
            },
            newkitchenkeynote:{
              
              size:'',
              type:'old',
              residue:false
            },
            keynote_update:true,
            kitchen_size:[],
            new_kitchen_size:[],
            old_kitchen_size:[],
            kitchen_keynotes:[],
            other_keynotes:[],
            final_keynotes:[],
            service_size:[],
            chair_size:[],
            sofa_size:[],
           progress:20,
           slotloader:false,
            services_list:[],
            url:'https://my.bleachkw.com'
         //  url:'http://localhost:8000'
            //url:'http://127.0.0.1:8000'
  },
  methods:{
   checkAll(){
    if(this.all_val){
        this.services_list=this.services
    }
    else{
      this.services_list=[]
    }
   },
   cancelServiceOrder(){
     var service_books=[]
     var requester_id=$('#user_id').val()
     for(var i=0;i<this.services_list.length;i++){
       service_books.push(this.services_list[i].id)
     }
    axios.post(this.url+'/customer/service/cancellrequest/',{
      service_books:service_books,
      requester_id:requester_id
    }).then(response=>{
     
      
      
    })
   },
   removeAll(){
     
    if(this.services.length==this.services_list.length){
      this.all_val=true
    }
    else{
      this.all_val=false
    }
   },
    getTheSize(service){
      var service_productivity=[]
      axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+service).then(response=>{
          this.productivity=response.data
          for(var i in this.productivity){
            
            service_productivity.push(this.productivity[i])
          }
          if(service=='Kitchen Cleaning'){
            this.kitchen_size=service_productivity
            this.formatKitchenSize()
          }
          
          
      })
    },
    removeInitialKitchenCost(){
      var totalKitchenCost=0
      for(var i=0;i<this.editSectionData.keynotes.length;i++){
        if(this.editSectionData.keynotes[i].sub_area=='kitchen'){
          var qty=JSON.parse(this.editSectionData.keynotes[i].quantity)
          totalKitchenCost=totalKitchenCost+qty.cost
          console.log("cost is"+qty.cost)
        }
      }
      this.fixed_section_cost=this.editSectionData.section_cost-totalKitchenCost
      console.log("fuixed cost is"+this.fixed_section_cost)
    },
    recalcKeynoteCost(){
      this.editSectionData.section_cost=this.fixed_section_cost
      console.log("called me"+JSON.stringify(this.kitchen_keynotes))
      for(var j=0;j<this.kitchen_keynotes.length;j++){
        this.editSectionData.section_cost=this.editSectionData.section_cost+this.kitchen_keynotes[j].quantity.size.cost
      }
    },
    addKitchenToKeynote(){
     
      this.kitchen_keynotes.push({
        sub_area:"kitchen",
        quantity:{
          size:this.newkitchenkeynote.size,
          max_size:this.newkitchenkeynote.size.max_size,
          type:this.newkitchenkeynote.type,
          residue:this.newkitchenkeynote.residue,
          cost:this.newkitchenkeynote.size.cost
        }
      })
      this.newkitchenkeynote={
        sub_area:'',
        quantity:{
          size:{},
          
          type:'old',
          residue:false,


        }
      }
      this.recalcKeynoteCost()
      
      
    },
    removeKitchen(index){
      this.kitchen_keynotes.splice(index,1)
      this.recalcKeynoteCost()
    },
    formatKitchenSize(){
      
      this.new_kitchen_size=[]
      this.old_kitchen_size=[]
      
        for(var i=0;i<this.kitchen_size.length;i++){
          this.kitchen_size[i].combined_size=this.kitchen_size[i].name+' ( '+this.kitchen_size[i].min_size+' sq.m - '+this.kitchen_size[i].max_size+' sq.m )'

          if(this.kitchen_size[i].is_newkitchen){

            this.new_kitchen_size.push(this.kitchen_size[i])
          }
          else{
            this.old_kitchen_size.push(this.kitchen_size[i])
          }
        }
        
      
    },
   /* formatFacadeSize(){
      
      this.highprice_facade=[]
      this.lowprice_facade=[]
      
        for(var i=0;i<this.service_productivity.length;i++){
         
          if(this.service_productivity[i].is_highprice_facade){
            this.highprice_facade.push(this.service_productivity[i])
          }
          else{
            this.lowprice_facade.push(this.service_productivity[i])
          }
        }
        
      
    },*/
   /* formatWindowSize(){
      
      this.new_kitchen_size=[]
      this.old_kitchen_size=[]
      
        for(var i=0;i<this.kitchen_size.length;i++){
         
          if(this.kitchen_size[i].is_newkitchen){
            this.new_kitchen_size.push(this.kitchen_size[i])
          }
          else{
            this.old_kitchen_size.push(this.kitchen_size[i])
          }
        }
        
      
    },*/
    addToKeynote(){
      this.keynote_update=false
      this.other_keynotes.push(this.newkeynote)
      this.keynote_update=true
      this.newkeynote={
        sub_area:'',
        quantity:''
      }
    },
    delKeynote(index){
      this.keynote_update=false
      this.other_keynotes.splice(index,1)
      this.keynote_update=true
    },
    checkSlot(index){
      if(this.selectedSlots.length>0){
       
       

        
          var prevSlot=index-1
          var nextSlot=index+1
          if(this.selectedSlots.includes(prevSlot)||this.selectedSlots.includes(nextSlot)){
            return true
          }
          else{
            return false
          }
        
      }
      else{
        return true
      }
    },
    selectSlot(index){
      this.selectedSlots.push(index)
    },
    removeSlot(index){
      var slotindex=this.selectedSlots.indexOf(index)
      this.selectedSlots.splice(slotindex,1)
    },
    parseOneTimeSlots(){
      this.parsedTimeSlots=[]
      for(var i in this.timeSlots){
        if(this.timeSlots[i].includes(2)){
          var slotNo=(parseInt(i)+2)/2
  
          this.parsedTimeSlots.push(this.slotFormat[String(slotNo)])
          
          
        }
      }
    },
    getSlotes(date){
      this.schedule_serviceTypes=[]
      this.selectedSlots=[]
      this.schedule_serviceTypes.push(this.service_type)
      this.slotloader=true
      axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:date,number_of_cleaners:this.selected_no_of_cleaners}
       
      )
      .then((response) => {
         this.timeSlots = response.data.slotes;
         this.parseOneTimeSlots()
         if(response.data.Error){
           this.errMsg=response.data['Error']
         }
         else{
           this.errMsg=''
         }
         this.slotloader=false
      

      })
       .catch((error) => {
        console.log(error);
      });
  
    },
    getSlotesByCleaners(){
      this.schedule_serviceTypes=[]
      this.selectedSlots=[]
      this.schedule_serviceTypes.push(this.service_type)
      this.slotloader=true
      if(!this.selected_cleaning_date){
        this.selected_cleaning_date=moment().format('DD-MM-YYYY')
      }
      axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:this.selected_cleaning_date,number_of_cleaners:this.selected_no_of_cleaners}
       
      )
      .then((response) => {
         this.timeSlots = response.data.slotes;
         this.parseOneTimeSlots()
         if(response.data.Error){
           this.errMsg=response.data['Error']
         }
         else{
           this.errMsg=''
         }
         this.slotloader=false
      

      })
       .catch((error) => {
        console.log(error);
      });
  
    },
    getVisitSlotes(date){
      this.schedule_serviceTypes=[]
      this.selectedSlots=[]
      this.schedule_serviceTypes.push(this.service_type)
      this.slotloader=true
      axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:date,number_of_cleaners:this.selected_no_of_cleaners}
       
      )
      .then((response) => {
        this.slotloader=false
         this.timeSlots = response.data.slotes;
         this.parseOneTimeSlots()
         if(response.data.Error){
           this.errMsg=response.data['Error']
         }
         else{
           this.errMsg=''
         }
      

      })
       .catch((error) => {
        console.log(error);
      });
  
    },
    resetVisit(){
      this.selectedSlots=[]
      this.schedule_id="",
      this.cleaning_date="",
       this.cleaning_time="",
       this.cleaning_hours="",
       this.no_of_cleaners="",
       this.selected_no_of_cleaners="",
       this.selectedSlots=[]
      this.setDate(moment().format('MM/DD/YYYY'))
    this.selected_date=moment().format('DD-MM-YYYY')
    $('#date_hidden').val(moment().format('MM/DD/YYYY'))
    },
   
    addVisit(){
      if(this.selectedSlots.length<1){
        this.visit_err='Please select atleast one slot'
      }
      else if(!this.selected_no_of_cleaners){
        this.visit_err='Please select the number of cleaners'
      }
      else{

      
      var minhour=Math.min(...this.selectedSlots)
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'add_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        cleaning_date:this.selected_date,
       cleaning_time:this.parsedTimeSlots[minhour].start_time,
       cleaning_hours:this.selectedSlots.length*2,
       no_of_cleaners:parseInt(this.selected_no_of_cleaners)
      }).then(response=>{
        $('#visit-close').click()
        location.reload()
       
      })
    }
    },
   
    deleteVisit(){
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'cancell_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        reduction_status:false,
       
        
      }).then(response=>{
       
        location.reload()
       
      })
    },
    cancelVisit(){
     
      if(this.reduction_status){
        var post_data={
          action_type:'cancell_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        reduction_status:this.reduction_status,
        reduction_amount:this.reducing_total,  
        }
      }
      else{
        var post_data={
          action_type:'cancell_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        reduction_status:this.reduction_status,
        }
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,post_data).then(response=>{
        
        location.reload()
       
      })
    },
    editVisit(){
      if(this.selectedSlots.length<1){
        this.visit_err='Please select atleast one slot'
      }
      else if(!this.selected_no_of_cleaners){
        this.visit_err='Please select the number of cleaners'
      }
      else{

      
      var minhour=Math.min(...this.selectedSlots)
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'edit_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        cleaning_date:this.selected_date,
       cleaning_time:this.parsedTimeSlots[minhour].start_time,
       cleaning_hours:this.selectedSlots.length*2,
       no_of_cleaners:parseInt(this.selected_no_of_cleaners)
      }).then(response=>{
        
        location.reload()
       
      })
    }
    },
    /*getOtherKeynotes(keynotes){
      var otherKeynotes
      for(var i=0;i<keynotes;i++){

      }
      if(keynote.sub_area=='kitchen')
    },*/
    getTheKitchens(){
      this.kitchen_keynotes=[]
      var kitchens=[]
      console.log("val is"+JSON.stringify(this.editSectionData))
      for(var i=0;i<this.editSectionData.keynotes.length;i++){
        if(this.editSectionData.keynotes[i].sub_area=='kitchen'){
          var keynote={
            sub_area:this.editSectionData.keynotes[i].sub_area,
            quantity:JSON.parse(this.editSectionData.keynotes[i].quantity)
          }
          if(keynote.quantity.type=='new'){
            for(var sz=0;sz<this.new_kitchen_size.length;sz++){
              if(this.new_kitchen_size[sz].name==keynote.quantity.size){
                keynote.quantity.size=this.new_kitchen_size[sz]
              }
            }
          }
          else if(keynote.quantity.type=='old'){
            for(var sz=0;sz<this.old_kitchen_size.length;sz++){
              if(this.old_kitchen_size[sz].name==keynote.quantity.size){
                keynote.quantity.size=this.old_kitchen_size[sz]
              }
            }
          }
          kitchens.push(keynote)
        }
       
      }
      console.log("quantity is"+JSON.stringify(kitchens))
      this.kitchen_keynotes=kitchens
      
    },
    getOtherKeynotes(){
      var others=[]
      this.other_keynotes=[]
      console.log("val is"+JSON.stringify(this.editSectionData))
      for(var i=0;i<this.editSectionData.keynotes.length;i++){
        if(this.editSectionData.keynotes[i].sub_area!='kitchen'){
          var keynote={
            sub_area:this.editSectionData.keynotes[i].sub_area,
            quantity:this.editSectionData.keynotes[i].quantity
          }
          others.push(keynote)
        }
       
      }
     
      this.other_keynotes= others
    },
    calDiscount(){
      this.paymentData.final_amount=this.total_amount-this.paymentData.discount
      this.paymentData.amount_after_cleaning=''
      this.paymentData.amount_before_cleaning=''
    },
    calcBreakdownBefore(){
      this.paymentData.amount_after_cleaning=this.paymentData.total_amount-this.paymentData.amount_before_cleaning
    },
    calcBreakdownAfter(){
      this.paymentData.amount_before_cleaning=this.paymentData.total_amount-this.paymentData.amount_after_cleaning
    },
    openPayment(){
      $('#edit-payment-tigger').click()
    },
    editSection(index,sid,service){
      this.action_type="Edit"
      this.service_type=$(service).data('service')
      console.log("index is"+index)
     // var sectiondata=$(section).data()
     this.editSectionData.section_id=sid
      console.log("section is "+JSON.stringify(this.sections[index-1]))
      this.sectionData=this.sections[index-1]
      if(this.service_type=='Facade Cleaning'){
        this.editSectionData.is_highprice_facade=this.sections[index-1].is_highprice_facade
        
      }
      $('#edit-dialog-tigger').click()
      this.editSectionData.section_cost=this.sectionData.section_cost
      this.editSectionData.section_name=this.sectionData.section_name
      
      
    },
    deleteSection(index,sid){
     
      console.log("index is"+index)
     // var sectiondata=$(section).data()
     this.deleteSectionData.section_id=sid
     /* console.log("section is "+JSON.stringify(this.sections[index-1]))
      this.sectionData=this.sections[index-1]*/
      $('#delete-section-tigger').click()
     
      
    },
    deleteTheSection(){
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'delete_section',
        section_id:this.deleteSectionData.section_id
      }).then(response=>{
        console.log(response)
        location.reload();
      })
    },

    
    changeCategory(){
      this.service_productivity=[]
     // this.editSectionData.size={}
      if(this.editSectionData.category=='Kitchen'){
        var service='Kitchen Cleaning'
        axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+service).then(response=>{
          this.productivity=response.data
          for(var i in this.productivity){
            if(!this.editSectionData.is_newkitchen && !this.productivity[i].is_newkitchen){
              this.service_productivity.push(this.productivity[i])
            }
            else if(this.editSectionData.is_newkitchen && this.productivity[i].is_newkitchen){
              this.service_productivity.push(this.productivity[i])
            }
           
          }
      })
      }
      else {
        this.getProductivity()
      }
    },
    updateDiscount(){
      if(this.paymentData.payment_method=='BREAKDOWN')
      {
       
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'edit_discount',
       "payment_method":this.paymentData.payment_method,
       "discount_amount":parseInt(this.paymentData.discount),
       "before_cleaning_amount":parseInt(this.paymentData.amount_before_cleaning),
       "after_cleaning_amount":parseInt(this.paymentData.amount_after_cleaning),
       
      }).then(response=>{
        console.log(response)
        $('#edit-payment-close').click()
        window.location.reload()
        
      })
    }
      else
      {
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'edit_discount',
       "payment_method":this.paymentData.payment_method,
       "discount_amount":parseInt(this.paymentData.discount),
       
       
      }).then(response=>{
        console.log(response)
        $('#edit-payment-close').click()
        window.location.reload()
      })
      }
      
    },
    parseKeynotes(){
      this.final_keynotes=[]
      for(var i=0;i<this.kitchen_keynotes.length;i++){
        this.final_keynotes.push({
          sub_area:'kitchen',
          quantity:JSON.stringify({
            cost:this.kitchen_keynotes[i].quantity.size.cost,
            max_size:this.kitchen_keynotes[i].quantity.size.max_size,
            residue:this.kitchen_keynotes[i].quantity.residue,
            type:this.kitchen_keynotes[i].quantity.type,
            size:this.kitchen_keynotes[i].quantity.size.name
          })
        })
      }
      for(var i=0;i<this.other_keynotes.length;i++){
        this.final_keynotes.push({
          sub_area:this.other_keynotes[i].sub_area,
          quantity:this.other_keynotes[i].quantity
        })
      }

    },
    resetKitchenSize(){
      this.editSectionData.size={}
    },
    resetFacadeSize(){
      this.editSectionData.size={}
    },
    updateSection(){
      this.parseKeynotes()
      var sectionData={}
      sectionData=
        {
          "section_name":this.editSectionData.section_name,
          "size":this.editSectionData.size.name,
          "wall_type":"",
          "ceiling_type":"",
          "floor_type":"",
          "cement_residue":false,
          "section_cost":this.editSectionData.section_cost,
          "section_net_cost":this.editSectionData.section_cost,
          "new_kitchen":this.editSectionData.new_kitchen,
          "oil_residue":this.editSectionData.oil_residue,
         "is_highprice_facade":false,
         "is_highprice_window":false,
      }
      if(this.service_type=='Upholstery Cleaning'){
        if(!this.editSectionData.size.name){
          sectionData.size=this.editSectionData.size+" Seater"
        }
      }
      
      if(this.editSectionData.wall_type.length>0){
        sectionData.wall_type=this.editSectionData.wall_type.join() 
        console.log("in wall type : "+this.editSectionData.wall_type)  
      }
      if(this.editSectionData.floor_type.length>0){
        sectionData.floor_type=this.editSectionData.floor_type.join()   
      }
      if(this.editSectionData.ceiling_type.length>0){
        sectionData.ceiling_type=this.editSectionData.ceiling_type.join()   
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'edit_section',
        "evaluation_book__id":this.eval_book_id,
        "section_details":sectionData,
        "keynotes":this.final_keynotes,
        "section_id":this.editSectionData.section_id,
      }).then(response=>{
        console.log(response)
        $('#edit-section-close').click()
        this.resetSection()
        location.reload()
      })
    },
    addSectionData(){
      var sectionData={}
     // this.other_keynotes=[]
     // this.kitchen_keynotes=[]
     this.parseKeynotes()
      sectionData=
        {
          "section_name":this.editSectionData.section_name,
          "size":this.editSectionData.size.name,
          "wall_type":"",
          "ceiling_type":"",
          "floor_type":"",
          "cement_residue":false,
          "section_cost":this.editSectionData.section_cost,
          "section_net_cost":this.editSectionData.section_cost,
          "new_kitchen":this.editSectionData.is_newkitchen,
         "is_highprice_facade":false,
         "is_highprice_window":false,
      }
      if(this.editSectionData.wall_type.length>0){
        sectionData.wall_type=this.editSectionData.wall_type.join()   
      }
      if(this.editSectionData.floor_type.length>0){
        sectionData.floor_type=this.editSectionData.floor_type.join()   
      }
      if(this.editSectionData.ceiling_type.length>0){
        sectionData.ceiling_type=this.editSectionData.ceiling_type.join()   
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'add_section',
        "evaluation_book__id":this.eval_book_id,
        "section_details":sectionData,
        "keynotes":this.final_keynotes
       
      }).then(response=>{
        console.log(response)
        $('#edit-section-close').click()
        this.resetSection()
      })
    },
    
    resetSection(){
      this.productivity={},
      this.service_productivity=[],
             this.editSectionData={
              size:{},
              area_type:[],
              section_cost:0,
              section_name:'',
              floor_type:[],
              ceiling_type:[],
              floor_type:[],
              material:[],
              category:'Floor',
              age:null,
              newkitchen:false
             },
             this.section_cost=0
             this.final_keynotes=[]
             this.other_keynotes=[]
             this.kitchen_keynotes=[]
              location.reload()   
    },
    getOrderId(){
      var orderId=window.location.href.split('/')[7]
      this.orderId=orderId
      console.log("orderid is"+orderId)

     
    },
    getSections(id){
      console.log("sectionid is"+id)
      console.log("data is"+JSON.stringify(this.sections[id]))
      
      this.currentSection=this.sections[id]
      this.gotSection=true
      return this.currentSection
    },
    calcSofaSize(){
     var found =false
     var sofa={}
      for(var i=0;i<this.sofa_size.length;i++){
        if(this.editSectionData.size<=this.sofa_size[i].max_size){
          found=true
          sofa=this.sofa_size[i]
          break;
        }
      }
      if(found){
        this.editSectionData.section_cost=sofa.cost
      }
      if(!found){
          var temp = this.sofa_size[this.sofa_size.length-1].cost
          var rem=parseInt(this.editSectionData.size)-this.sofa_size[this.sofa_size.length-1].max_size
          this.editSectionData.section_cost=temp+(rem*this.sofa_size[0].unit_price)
      }
      
    },
     getSection(id){
      this.eval_book_id=id
     
        axios.get(this.url+'/customer/editorder/'+this.orderId+'?evaluation_book_id='+id).then(response=>{
          this.sections=response.data.section_details.evaluationsection_book
          this.service_type=response.data.section_details.service_type.name
           this.service_size=[]
           this.chair_size=[]
           this.sofa_size=[]
           axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+this.service_type).then(response=>{
            var size=response.data
            for(var i in size){
              this.service_size.push(size[i])
              size[i].combined_size=size[i].name+' ( '+size[i].min_size+' sq.m - '+size[i].max_size+' sq.m )'
              if(size[i].upholstery_type=='CHAIR'){
                

                this.chair_size.push(size[i])
              }
              else if(size[i].upholstery_type=='SOFA')
              {
                this.sofa_size.push(size[i])
              }
            }
            console.log("size is"+JSON.stringify(this.service_size))
          /* old order size conversion */
              

          /* new order size conversion begins here */
        
           /* General cleaning  size conversion */ 
          if(this.service_type=='General Cleaning' || this.service_type=='Deep Cleaning' || this.service_type=='Storage Area' || this.service_type=='Sterilization'|| this.service_type=='Carpet Cleaning'|| this.service_type=='Car Parking Umbrella' || this.service_type=='Outdoor Cleaning'){
            for(var j=0;j<this.sections.length;j++){
             
              for(var i=0;i<this.service_size.length;i++){
                if(parseInt(this.sections[j].size)){
                  var section_size=parseInt(this.sections[j].size)
                  if(section_size<=this.service_size[i].max_size && section_size>=this.service_size[i].min_size){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                else{
                  if(this.service_size[i].name==this.sections[j].size){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                
              }
            }
              
          }
          /* Upholstery cleaning  size conversion */ 
          if(this.service_type=='Upholstery Cleaning'){
           var type=""
            for(var j=0;j<this.sections.length;j++){
              if(this.sections[j].size.includes('Seater')){
                type="SOFA"
                //this.sections[j].size=this.this.sections[j].size.split(" ")[0]
                this.sections[j].size=this.sections[j].size.split(" ")[0]
                console.log("section size is "+this.sections[j].size.split(" ")[0])
                this.sections[j].upholstery_type="SOFA"
              }
              else{
                type="CHAIR"
                this.sections[j].upholstery_type="CHAIR"
              }
              console.log("type is"+type)
              if(type=="CHAIR"){
                for(var i=0;i<this.service_size.length;i++){
                  if(this.service_size[i].upholstery_type=="SOFA" && this.sections[j].size==this.service_size[i].name){
                    
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
              }
             
            }
              
          } 
         /* kitchen cleaning */
         if(this.service_type=='Kitchen Cleaning'){
        
           for(var j=0;j<this.sections.length;j++){
            
             
            
             if(this.sections[j].new_kitchen){
               for(var i=0;i<this.service_size.length;i++){
                if(parseInt(this.sections[j].size)){
                  var section_size=parseInt(this.sections[j].size)
                  if(section_size<=this.service_size[i].max_size && section_size>=this.service_size[i].min_size && this.service_size[i].is_newkitchen){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                else{
                 if(this.service_size[i].is_newkitchen && this.sections[j].size==this.service_size[i].name){
                   
                   this.sections[j].size=this.service_size[i]
                  
                 }
                }
               }
             }
             else{
              for(var i=0;i<this.service_size.length;i++){
                if(parseInt(this.sections[j].size)){
                  var section_size=parseInt(this.sections[j].size)
                  if(section_size<=this.service_size[i].max_size && section_size>=this.service_size[i].min_size && !this.service_size[i].is_newkitchen){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                else{
                if(!this.service_size[i].is_newkitchen && this.sections[j].size==this.service_size[i].name){
                  
                  this.sections[j].size=this.service_size[i]
                 
                }
              }
            }
             }
            
           }
             
         }
         
         /** Facade Cleaning */
         if(this.service_type=='Facade Cleaning'){
           this.highprice_facade=[]
           this.lowprice_facade=[]
          for(var i=0;i<this.service_size.length;i++){
            
            if(this.service_size[i].is_highprice_facade){
              this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
              this.highprice_facade.push(this.service_size[i])
            }
            else{
              this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
              this.lowprice_facade.push(this.service_size[i])
            }
            
          }
        
          for(var j=0;j<this.sections.length;j++){
           
            
           
            if(this.sections[j].is_highprice_facade){
             
              for(var i=0;i<this.service_size.length;i++){
                if(this.service_size[i].is_highprice_facade && this.sections[j].size==this.service_size[i].name){
                  
                  this.sections[j].size=this.service_size[i]
                 
                }
                
                
              }
            }
            else{
             for(var i=0;i<this.service_size.length;i++){
               if(!this.service_size[i].is_highprice_facade && this.sections[j].size==this.service_size[i].name){
                 
                 this.sections[j].size=this.service_size[i]
                
               }
               
             }
            }
           
          }
            
        }
        /** window cleaning */
        if(this.service_type=='Window Cleaning'){
        
          for(var j=0;j<this.sections.length;j++){
           
            
           
            if(this.sections[j].is_highprice_window){
              for(var i=0;i<this.service_size.length;i++){
                if(this.service_size[i].is_highprice_window && this.sections[j].size==this.service_size[i].name){
                  
                  this.sections[j].size=this.service_size[i]
                 
                }
                if(this.service_size.is_highprice_window){
                  this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
                  this.highprice_window.push(this.service_size[i])
                }
                else{
                  this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
                  this.lowprice_window.push(this.service_size[i])
                }
              }
            }
            else{
             for(var i=0;i<this.service_size.length;i++){
               if(!this.service_size[i].is_highprice_window && this.sections[j].size==this.service_size[i].name){
                 
                 this.sections[j].size=this.service_size[i]
                
               }
             }
            }
           
          }
            
        }
        })
          
        }).catch(err=>{
          console.log(err)
        })
    },
    onChange(event) {
      if(event.target.value == "BREAKDOWN"){
        this.breakDownFlag= true
      }else{
        this.breakDownFlag =false
      }
      console.log(this.amount)
  },
  calcSectionCost(){
   
    this.editSectionData.section_cost=this.editSectionData.size.cost
    this.fixed_section_cost=this.editSectionData.section_cost
    this.recalcKeynoteCost()
  },
    setDate(d){
    
      this.soltdate =  new Date(d)
      var todaysDate = new Date(d)
      todaysDate = new Date(d).toDateString().split(" ");
      this.year = todaysDate[3]
      this.day = todaysDate[0]+", "+todaysDate[1]+" "+todaysDate[2]
    },
    resetContacts(){
      this.contacts=[]
    },
    getProductivity(){
      this.service_productivity=[]
      axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+this.service_type).then(response=>{
          this.productivity=response.data
          for(var i in this.productivity){
            this.productivity[i].combined_size=this.productivity[i].name+' ( '+this.productivity[i].min_size+' sq.m - '+this.productivity[i].max_size+' sq.m )'

            this.service_productivity.push(this.productivity[i])
          }
          if(this.service_type=='Kitchen Cleaning'){
            this.formatKitchenSize()
          }
         
      })
    },
    async getServiceSize(){
    
      this.service_size=[]
      await axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+this.service_type).then(response=>{
          var size=response.data
          for(var i in size){
            this.service_size.push(size[i])
          }
         
         
      }
      )
      return this.service_size
    },
    parseUpholstery(){
      if(this.editSectionData){}
    }
  }
 
});

