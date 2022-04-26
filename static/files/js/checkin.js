var url=api
const app = new Vue({
  el: "#app",
  delimiters: ["<%", "%>"],
  data: {
    imageData: [],
    images:[],
    absent_list:[],
    ImageDetails: {
        url: "",
        file: "",
        service:""
      },
      cleaningData:{
        cleaningteam_id:null,
        cleaningtype:null,
        cleaningpolicy:null,
        teamcount:null,
        remainingteamcount:null
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
    openCheckin(cleaningteam_id,cleaningtype,cleaningpolicy,teamcount,remainingteamcount){

      $('#cleaner-popup-btn').click()
      this.cleaningData.cleaningteam_id=cleaningteam_id
      this.cleaningData.cleaningtype=cleaningtype
      this.cleaningData.cleaningpolicy=cleaningpolicy
      this.cleaningData.teamcount=teamcount
      this.cleaningData.remainingteamcount=remainingteamcount
    },
    checkinBackup(team_id){
      console.log("team id is"+team_id)
      $('#backup-cleaner-popup-btn').click()
      this.cleaningData.cleaningteam_id=team_id
    },
    checkinBackupTeam(){
      
        axios.post(url+'/api/backup-check-in/',{
          team_id:this.cleaningData.cleaningteam_id,
          absent_list:this.absent_list
        }).then(response=>{
          if(response.data.success){
            location.reload()
          }

        })
    },
    submitform(cleaningteam_id,cleaningtype,cleaningpolicy,teamcount,remainingteamcount){
     

    if (cleaningtype == 'check-in'){

      var form_items = {
        'team_id':cleaningteam_id,
        'check_in_notes' : $('#check_in_notes').val(),
        'absent_list': this.absent_list,
      }

      for(var i=0;i<this.imageData.length;i++){

        form_items.append('media',this.imageData[i].file)
        
      }
      var form_url = url+'/api/check-in/' ;
    }else{

      var form_items = {
        'team_id':cleaningteam_id,
        'check_out_notes':$('#check_out_notes').val()
      }

      for(var i=0;i<this.imageData.length;i++){

        form_items.append('media',this.imageData[i].file)
        
      }

      var keynote_count = $('.keynote:checkbox').length;
      var checked_keynotes = $('.keynote:checkbox:checked').length;
      
      console.log(keynote_count,checked_keynotes,"keyns")

      if (cleaningpolicy == 'SUBSCRIPTION'){
        if(checked_keynotes == keynote_count){
          var form_url = url+'/api/check-out/' ;
        }else{
          alert("Please check all keynotes !")
        }
      }
      
      if (cleaningpolicy == 'ONE TIME SERVICE'){
        console.log(remainingteamcount,teamcount,"loc")
        if (remainingteamcount == 1 && teamcount > 1){
          
          if(checked_keynotes == keynote_count){
            var form_url = url+'/api/check-out/' ;
          }else{
            alert("Please check all keynotes !")
          }

        }
        
        if (remainingteamcount == 1 && teamcount == 1){
          if(checked_keynotes == keynote_count){
            var form_url = url+'/api/check-out/' ;
          }else{
            alert("Please check all keynotes !")
          }
        }
        
        if (remainingteamcount > 1 && teamcount > 1){
          var form_url = url+'/api/check-out/' ;
        }
      }
      
    };

    console.log(form_items,"formitms")
     
    if (this.imageData.length > 0){

      console.log(cleaning_images,"testdata")
      console.log(form_items,"form itesmss")

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

  },

    submitCheckinform(){
      var cleaningteam_id=this.cleaningData.cleaningteam_id
      var cleaningtype=this.cleaningData.cleaningtype
      var cleaningpolicy=this.cleaningData.cleaningpolicy
      var teamcount=this.cleaningData.teamcount
      var remainingteamcount=this.cleaningData.remainingteamcount

      

    if (cleaningtype == 'check-in'){
      var form_items = {
        'team_id' : cleaningteam_id,
        'check_in_notes':$('#check_in_notes').val(),
        'absent_list':this.absent_list
      }

      for(var i=0;i<this.imageData.length;i++){

        form_items.append('media',this.imageData[i].file)
        
      }

      var form_url = url+'/api/check-in/' ;
    }else{
      var form_items = {
        'team_id' : cleaningteam_id,
        'check_out_notes':$('#check_out_notes').val()
      }

      for(var i=0;i<this.imageData.length;i++){

        form_items.append('media',this.imageData[i].file)
        
      }

      var keynote_count = $('.keynote:checkbox').length;
      var checked_keynotes = $('.keynote:checkbox:checked').length;
      form_items.append('check_out_notes',$('#check_out_notes').val())
      console.log(keynote_count,checked_keynotes,"keyns")

      if (cleaningpolicy == 'SUBSCRIPTION'){
        if(checked_keynotes == keynote_count){
          var form_url = url+'/api/check-out/' ;
        }else{
          alert("Please check all keynotes !")
        }
      }
      
      if (cleaningpolicy == 'ONE TIME SERVICE'){
        console.log(remainingteamcount,teamcount,"loc")
        if (remainingteamcount == 1 && teamcount > 1){
          
          if(checked_keynotes == keynote_count){
            var form_url = url+'/api/check-out/' ;
          }else{
            alert("Please check all keynotes !")
          }

        }
        
        if (remainingteamcount == 1 && teamcount == 1){
          if(checked_keynotes == keynote_count){
            var form_url = url+'/api/check-out/' ;
          }else{
            alert("Please check all keynotes !")
          }
        }
        
        if (remainingteamcount > 1 && teamcount > 1){
          var form_url = url+'/api/check-out/' ;
        }
      }
      
    };
     
    if (this.imageData.length > 0){
      console.log(cleaning_images,"testdata")
      console.log(form_items,"form itesmss")

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



$(".action-icon").click(function(){
  console.log("celd")
  $(this).toggleClass("down2")  ; 
})
function changeState(item,cleaner){
  console.log("cleaner is"+cleaner)
  if($(item).hasClass('clr-check-box-active')){
    $(item).removeClass('clr-check-box-active')
    $(item).addClass('clr-check-box')
    if(!app.absent_list.includes(cleaner)){
      app.absent_list.push(cleaner)
    }
  }
  else{
    $(item).removeClass('clr-check-box')
    $(item).addClass('clr-check-box-active')
    if(app.absent_list.includes(cleaner)){
      var index=app.absent_list.indexOf(cleaner)
        app.absent_list.splice(index,1)
      
    }
  }
}