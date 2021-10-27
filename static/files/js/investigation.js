const app = new Vue({
    el: "#app",   
    delimiters: ["<%", "%>"],
    data () {
          return {
              addfollow:true,
            imageData: [],
            images:[],
            ImageDetails: {
                url: "",
                file: "",
                service:""
            },
          }
    },
    methods:{
        changeFollowup(val){
            if(val == 'yes'){
                this.addfollow = true
            }else{
                this.addfollow = false
            }
            console.log(this.addfollow)
        },
        showFl(){
            console.log(this.addfollow)
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
});
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