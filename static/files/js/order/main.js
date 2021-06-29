

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
  
}
const app = new Vue({
  el: "#app",
  
  delimiters: ["<%", "%>"],
  
  mounted() {
    
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
             ]
  },
  methods:{
    onChange(event) {
      if(event.target.value == "BREAKDOWN"){
        this.breakDownFlag= true
      }else{
        this.breakDownFlag =false
      }
      console.log(this.amount)
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
    }
  }
 
});

