

$(document).ready(function () {
  $("#content-slider").lightSlider({

          item:2,
          loop:true,
          slideMove:1,
          speed:600,
         
  });
  $('#calendar').datepicker({
    language: "en",
    
  });
  
  $('#calendar').on('changeDate', function() {
    $('#date_hidden').val(
        $('#calendar').datepicker('getFormattedDate')
    );
    console.log($('#date_hidden').val()) 
    app.setDate($('#date_hidden').val())
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
function editSection(section){
  console.log("i m here")
  var sectiondata=$(section).data()
  console.log("section is "+JSON.stringify(sectiondata))
  app.sectionData=sectiondata
  $('#edit-dialog-tigger').click()
  app.editSectionData.section_cost=sectiondata.section_cost
  app.editSectionData.section_name=sectiondata.section_name
  
}
function editService(service){
  app.service_type=$(service).data('service')
  app.edit=true
  app.getProductivity()
  
}
const app = new Vue({
  el: "#app",
  
  delimiters: ["<%", "%>"],
  
  mounted() {
    this.getOrderId()
  },
  components: { Multiselect: window.VueMultiselect.default },

  data: {
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
    options: [
               {
                 "city": "San Martin",
                 "city_ascii": "San Martin",
                 "lat": -33.06998533,
                 "lng": -68.49001612,
                 "pop": 99974,
                 "country": "Argentina",
                 "iso2": "AR",
                 "iso3": "ARG",
                 "province": "Mendoza",
                 "timezone": "America/Argentina/Mendoza"
               },
               {
                 "city": "San Nicolas",
                 "city_ascii": "San Nicolas",
                 "lat": -33.33002114,
                 "lng": -60.24000289,
                 "pop": 117123.5,
                 "country": "Argentina",
                 "iso2": "AR",
                 "iso3": "ARG",
                 "province": "Ciudad de Buenos Aires",
                 "timezone": "America/Argentina/Buenos_Aires"
               },
               {
                 "city": "San Francisco",
                 "city_ascii": "San Francisco",
                 "lat": -31.43003375,
                 "lng": -62.08996749,
                 "pop": 43231,
                 "country": "Argentina",
                 "iso2": "AR",
                 "iso3": "ARG",
                 "province": "Córdoba",
                 "timezone": "America/Argentina/Cordoba"
               }
             ],
             productivity:{},
             editSectionData:{
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
             section_cost:0,
             orderId:'',
             sections:[],
             currentSection:[],
             gotSection:false,
             url:'http://localhost:8000',
             eval_book_id:'',
             action_type:''
  },
  methods:{
    editSection(index,sid){
      this.action_type="Edit"
      console.log("index is"+index)
     // var sectiondata=$(section).data()
     this.editSectionData.section_id=sid
      console.log("section is "+JSON.stringify(this.sections[index-1]))
      this.sectionData=this.sections[index-1]
      $('#edit-dialog-tigger').click()
      this.editSectionData.section_cost=this.sectionData.section_cost
      this.editSectionData.section_name=this.sectionData.section_name
      
    },
    addSection(index){
      this.action_type="Add"
      $('#edit-dialog-tigger').click()
    },
    changeCategory(){
      this.service_productivity=[]
      this.editSectionData.size={}
      if(this.editSectionData.category=='Kitchen'){
        var service='Kitchen Cleaning'
        axios.get('https://test.bleach-kw.com/customer/ajax/getservicesizeprice?service_type='+service).then(response=>{
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
    updateSection(){
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
        this.sectionData.wall_type=this.editSectionData.wall_type.join()   
      }
      if(this.editSectionData.floor_type.length>0){
        this.sectionData.wall_type=this.editSectionData.floor_type.join()   
      }
      if(this.editSectionData.ceiling_type.length>0){
        this.sectionData.wall_type=this.editSectionData.ceiling_type.join()   
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'edit_section',
        "evaluation_book__id":this.eval_book_id,
        "section_details":sectionData,
        "section_id":this.editSectionData.section_id,
      }).then(response=>{
        console.log(response)
        $('#edit-section-close').click()
        this.resetSection()
      })
    },
    addSection(){
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
        this.sectionData.wall_type=this.editSectionData.wall_type.join()   
      }
      if(this.editSectionData.floor_type.length>0){
        this.sectionData.wall_type=this.editSectionData.floor_type.join()   
      }
      if(this.editSectionData.ceiling_type.length>0){
        this.sectionData.wall_type=this.editSectionData.ceiling_type.join()   
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
    getSection(id){
      this.eval_book_id=id
        axios.get('http://localhost:8000/customer/editorder/'+this.orderId+'?evaluation_book_id='+id).then(response=>{
          this.sections=response.data.section_details.evaluationsection_book
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
      axios.get('https://test.bleach-kw.com/customer/ajax/getservicesizeprice?service_type='+this.service_type).then(response=>{
          this.productivity=response.data
          for(var i in this.productivity){
            this.service_productivity.push(this.productivity[i])
          }
      })
    }
  }
 
});

