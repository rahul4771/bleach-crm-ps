let app = new Vue({
    el: "#app",
    components: { Multiselect: window.VueMultiselect.default },
    delimiters: ["<%", "%>"],
    data () {
          return {
            edit_section:null,
            edit_section_active_index:null,
            edit_servicetype:'',
            cleaningsections:null,
            selectedDate: new Date(),
              addfollow:true,
            imageData: [],
            images:[],
            ImageDetails: {
                url: "",
                file: "",
                service:""
            },
            render:true,
            time_slots:[
                {
          start_time:'12:00 AM',
          end_time:'02:00 AM'
        },{
          start_time:'02:00 AM',
          end_time:'04:00 AM'
        },
        {
          start_time:'04:00 AM',
          end_time:'06:00 AM'
        },
        {
          start_time:'06:00 AM',
          end_time:'08:00 AM'
        },
        {
          start_time:'08:00 AM',
          end_time:'10:00 AM'
        },
        {
          start_time:'10:00 AM',
          end_time:'12:00 PM'
        },
        {
          start_time:'12:00 PM',
          end_time:'02:00 PM'
        },
        {
          start_time:'02:00 PM',
          end_time:'04:00 PM'
        },
        {
          start_time:'04:00 PM',
          end_time:'06:00 PM'
        },
        {
          start_time:'06:00 PM',
          end_time:'08:00 PM'
        },
        {
          start_time:'08:00 PM',
          end_time:'10:00 PM'
        },
        {
          start_time:'10:00 PM',
          end_time:'12:00 AM'
        }
                ],
                selected_slots:[]
          }
    },
    methods:{
        editSection(item){
            console.log(item)
            this.edit_section_active_index = item
            this.edit_section = this.cleaningsections[item]
            $('#edit-dialog-tigger').click();
        },
        removeSelected(item){
            var index = this.selected_slots.indexOf(item);
            if (index !== -1) {
                this.selected_slots.splice(index, 1);
              }
        },
        checkSelected(index){
            return this.selected_slots.includes(index)
            
        },
        addSlot(start,end,slot){
            this.render=false
            this.selected_slots.push(slot);
            this.render=true
          },
        changeFollowup(val){
            if(val == 'yes'){
                this.addfollow = true
            }else{
                this.addfollow = false
            }
           
        },
        deleteImage(imageindex) {
            this.imageData.splice(imageindex, 1);
            this.images.splice(imageindex, 1);
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
            console.log(this.imageData)
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

    }
})
$(document).ready(function () {
    $(".owl-carousel").owlCarousel({
    items: 2,
    nav: true,
    margin: 10,
    responsive:{
        0:{
            items:1
        },
        600:{
            items:2
        },
        1000:{
            items:4
        }
    },
    navText: [
      `<i style="color:#707070;" class='fa fa-chevron-left service-control' @click='prevService()'></i>`,
      `<i style="color:#707070;" class='fa fa-chevron-right service-control'></i>`,
    ],
  });
});

function showCleaners(){
    //$('#id_cl').click();
}
function DropDown(el) {
    this.dd = el;
    this.placeholder = this.dd.children('span');
    this.opts = this.dd.find('ul.drop li');
    this.val = '';
    this.index = -1;
    this.initEvents();
}

   
DropDown.prototype = {
    initEvents: function () {
        var obj = this;
        obj.dd.on('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).toggleClass('active');
        });
        obj.opts.on('click', function () {
            var opt = $(this);
            obj.val = opt.text();
            obj.index = opt.index();
            obj.placeholder.text(obj.val);
            opt.siblings().removeClass('selected');
            opt.filter(':contains("' + obj.val + '")').addClass('selected');
        }).change();
    },
    getValue: function () {
        return this.val;
    },
    getIndex: function () {
        return this.index;
    }
};

$(function () {
    // create new variable for each menu
    var dd1 = new DropDown($('#noble-gases'));
    

    // var dd2 = new DropDown($('#other-gases'));
    $(document).click(function () {
        // close menu on document click
        $('.wrap-drop').removeClass('active');
    });
});