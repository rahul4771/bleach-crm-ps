var url=api
const app = new Vue({
  el: "#app",
  delimiters: ["<%", "%>"],
  data: {
    imageData: [],
    images:[],
    ImageDetails: {
        url: "",
        file: "",
        service:""
      },
  },
  methods: {
    deleteImage(imageindex) {
      this.imageData.splice(imageindex, 1);
    },
    uploadImgToArray(file,fileName){
        file.lastModifiedDate = Date.now();
      
      var converted_file = new File([file],  fileName,{lastModified: Date.now()});
        console.log("file size is "+converted_file.size)
        this.ImageDetails.url = URL.createObjectURL(converted_file);
        this.ImageDetails.file = converted_file;
        this.imageData.push(this.ImageDetails);
        this.images.push(converted_file);
        this.ImageDetails = {
          file: "",
          url: "",
          service:""
          
        };
      },
    async onImageFileChanged(event) {
      console.log(event);
      console.log("orginal file size is" + event.target.files[0].size);
      console.log(this.imageData,this.images,"imgd");
      var file = event.target.files[0];

      const options = {
        maxSizeMB: 1,
        maxWidthOrHeight: 1920,
        useWebWorker: true,
        onProgress: Function(2),
      };
      try {
        const compressedFile = await imageCompression(
          event.target.files[0],
          options
        );
        console.log(
          "compressedFile instanceof Blob",
          compressedFile instanceof Blob
        ); // true
        console.log(
          `compressedFile size ${compressedFile.size / 1024 / 1024} MB`
        ); // smaller than maxSizeMB

        await this.uploadImgToArray(compressedFile, event.target.files[0].name); // write your own logic
      } catch (error) {
        console.log(error);
      }
    },

    submitform(cleaningteam_id,cleaningtype){
      //console.log(cleaningteam_id,cleaningtype,"lop")
      var form_items = new FormData()
      form_items.append('team_id',cleaningteam_id)

    for(var i=0;i<this.imageData.length;i++){
      form_items.append('media',this.imageData[i].file);
      }

    if (cleaningtype == 'check-in'){
      form_items.append('check_in_notes',$('#check_in_notes').val())
      var form_url = url+'/api/check-in/' ;
    }else{
      var keynote_count = document.querySelectorAll('input[type="checkbox"]').length;
      var checked_keynotes = document.querySelectorAll('input[type="checkbox"]:checked').length;
      form_items.append('check_out_notes',$('#check_out_notes').val())
      console.log(keynote_count,checked_keynotes,"keyns")

      if(checked_keynotes == keynote_count){
        var form_url = url+'/api/check-out/' ;
      }else{
        alert("Please check all keynotes !")
      }
      
    };
     
    if (this.imageData.length > 0){
        axios.post(
          form_url, form_items
        
       )
       .then((response) => {
         
         console.log(response)
         if (response.data.success == true){
          window.location.href='/tl/dashboard/?my_cleaning_calendar_date='+response.data.cleaning_date+'';
         }
       
        
       })
        .catch((error) => {
         console.log(error,"rok");
       
       });

      }else{
        alert("Please add before cleaning images !")
      }

  }

  },

});

$('.owl-carousel').owlCarousel({
  
  items: 1,
  nav: true,
  loop:true,
  autoplay:false,
autoplayTimeout:2000,
autoplayHoverPause:false,
  navText: [
      `<i style="color:#000000 !important;" class='fa fa-chevron-left service-control' @click='prevService()'></i>`,
      `<i style="color:#000000 !important;"  class='fa fa-chevron-right service-control'></i>`,
  ],
});
$('.play').on('click',function(){
  owl.trigger('play.owl.autoplay',[1000])
})
$('.stop').on('click',function(){
  owl.trigger('stop.owl.autoplay')
})



// $(".action-icon").click(function(){
//   console.log("celd")
//   $(this).toggleClass("down2")  ; 
// })
