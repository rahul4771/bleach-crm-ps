

$(document).ready(function () {
    /* $("#content-slider").lightSlider({
   
             item:2,
             loop:true,
             slideMove:1,
             speed:600,
            
     });*/
     $('#calendar').datepicker({
       language: "en",
       
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
     //app.getProductivity()
     console.log("index is"+index)
    // var sectiondata=$(section).data()
    app.getSection(eval_book_id)
    app.editSectionData.section_id=sid
   
    app.editSectionData.keynotes=app.sections[index-1].keynotesections
     console.log("section is "+JSON.stringify(app.sections[index-1]))
     app.sectionData=app.sections[index-1]
     app.getOtherKeynotes()
         app.getTheKitchens()
        
         app.recalcKeynoteCost()
     $('#edit-dialog-tigger').click()
     app.editSectionData.section_cost=app.sectionData.section_cost
     app.editSectionData.section_name=app.sectionData.section_name
     app.removeInitialKitchenCost()
     if(app.sectionData.wall_type!="")
     {
       app.editSectionData.wall_type=app.sectionData.wall_type.split(',')
     }
     if(app.sectionData.floor_type!="")
     {
       app.editSectionData.floor_type=app.sectionData.floor_type.split(',')
     }
     if(app.sectionData.ceiling_type!="")
     {
       app.editSectionData.ceiling_type=app.sectionData.ceiling_type.split(',')
     }
     if(app.sectionData.materials!="")
     {
       app.editSectionData.materials=app.sectionData.materials.split(',')
     }
     
     
     
     
     app.findSize()
     
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
     app.getSlotes(app.cleaning_start_date)
     $('#date_hidden').val((moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY')))
     $("#calendar").datepicker("update", moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY'));
     app.setDate(moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY'))
     
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
         "is_newkitchen":false,
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
      
       
     },
     components: { Multiselect: window.VueMultiselect.default },
   
     data: {
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
                 is_newkitchen:false
                },
                section_cost:0,
                orderId:'',
                sections:[],
                currentSection:[],
                gotSection:false,
                //url:'http://localhost:8000',
                url:'https://test.bleach-kw.com',
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
               //url:'https://test.bleach-kw.com'
               url:'http://localhost:8000'
     },
     methods:{
      
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
            
             if(this.kitchen_size[i].is_newkitchen){
               this.new_kitchen_size.push(this.kitchen_size[i])
             }
             else{
               this.old_kitchen_size.push(this.kitchen_size[i])
             }
           }
           
         
       },
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
         axios
         .post(
            this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:date,number_of_cleaners:this.no_of_cleaners}
          
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
         
   
         })
          .catch((error) => {
           console.log(error);
         });
     
       },
       getVisitSlotes(date){
         this.schedule_serviceTypes=[]
         this.selectedSlots=[]
         this.schedule_serviceTypes.push(this.service_type)
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
           $('#visit-close').click()
          // location.reload()
          
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
             "is_newkitchen":this.editSectionData.is_newkitchen,
            "is_highprice_facade":false,
            "is_highprice_window":false,
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
         this.other_keynotes=[]
         this.kitchen_keynotes=[]
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
             "is_newkitchen":this.editSectionData.is_newkitchen,
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
                 is_newkitchen:false
                },
                this.section_cost=0
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
       async getSection(id){
         this.eval_book_id=id
        
           axios.get(this.url+'/customer/editorder/'+this.orderId+'?evaluation_book_id='+id).then(response=>{
             this.sections=response.data.section_details.evaluationsection_book
             this.service_type=response.data.section_details.service_type.name
             var servicesize= await this.getServiceSize()
             
             console.log("productivy is"+JSON.stringify(this.service_productivity))
             if(this.service_type=='General Cleaning'){
               for(var j=0;j<this.sections.length;j++){
                 for(var i=0;i<servicesize.length;i++){
                   if(servicesize[i].name==this.sections[j].size){
                     this.sections[j].size=servicesize[i]
                    
                   }
                 }
               }
                 
             }
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
               this.service_productivity.push(this.productivity[i])
             }
            
         })
       },
       async getServiceSize(){
         this.service_productivity=[]
         await axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+this.service_type).then(response=>{
             var size=response.data
             for(var i in size){
               this.service_size.push(this.size[i])
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
   
   