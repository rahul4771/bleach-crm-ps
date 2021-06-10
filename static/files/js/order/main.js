

$(document).ready(function () {
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




function myFunction() {
  document.getElementById("visti-section").classList.toggle("not-show");
  document.getElementById("myDropdown").classList.toggle("show");
}
function onClick(element) {
  document.getElementById("img01").src = element.src;
  document.getElementById("modal01").style.display = "block";
}
const app = new Vue({
  el: "#app",
  delimiters: ["<%", "%>"],
  
  mounted() {
    
  },
  
  data: {
    soltdate: null, 
    edit: false,
    cancelDialog:false,
    year:null,
    day:null,
    month:null,
    paymentType:"",
    key: "",
    breakDownFlag:false,
    amount:""
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
    }
  }
 
});

