

    $(document).ready(function(){
        $('#schedule_list_id').hide();
    })





  const app = new Vue({
  el: "#app",
  components: { Multiselect: window.VueMultiselect.default },
     
  delimiters: ["<%", "%>"],
  data () {
        return {
            
            edit_section_active_index:null,
            edit_servicetype:'',
            isOrderSelected:true,
            cleaningsections:null,
            paybackSerDetials:'',
            paybackSerPrice:'',
            paybackSer:[],
            paybackDamDetials:'',
            paybackDamPrice:'',
            paybackDam:[],
            paybackOtherDetials:'',
            paybackOtherPrice:'',
            paybackOther:[],
            paybackaction:['Service Quality','Damage','Other'],
            payback:[],
            reporttitile:'',
            reportnote:'',
            userselect:'',
            damagenote:'',
            key:1,
            damacval:[],
            seracval:"",
            atAc:"",
            atStaff:"",
            ticketAction:[
                {
                    id:1,
                    selected:false,
                    name:'Payback'
                },
                {
                    id:2,
                    selected:false,
                    name:'Internal Report'
                },
                {
                    id:3,
                    selected:false,
                    name:'Assign Investigator'
                },
                // {
                //     id:4,
                //     selected:false,
                //     name:'Insurance Request'
                // },
                // {
                //     id:5,
                //     selected:false,
                //     name:'Follow-up Cleaning'
                // },
            ],
            damAc:['Payback','Internal Report','Assign Investigator','Insurance Request','Follow-up Cleaning'],
            damAc2 : ['Payback','Gift','Assign Investigator','Follow-up Cleaning'],
            damAc3:[],
            ac: ['Gift', 'Internal reporting'],
            ac2: ['name', 'Name'],
            at:false,
            dam:false,
            ser:false,

            active:true,
          value: [],
          options:[
            { name: 'Damage', id: 1 , selected:false},
            { name: 'Service Quality', id: 2, selected:false },
            { name: 'Attitude & Behaviour', id: 3, selected:false },
          ],
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
        editSection(item){
            console.log(item)
            this.edit_section_active_index = item
            this.edit_section = this.cleaningsections[item]
            $('#edit-dialog-tigger').click();
        },
        removeFromPayback(){
            // console.log('ghj')
            // if(!this.payback.includes('Service Quality')){
            //     this.paybackSer = []
            // }
            // if(!this.payback.includes('Damage')){
            //     this.paybackDam = []
            // }
            // if(!this.payback.includes('Other')){
            //     this.paybackOther = []
            // }
        },
        removePayback(item){
            console.log(item)
            //Service Quality','Damage','Other'],
            if(item == 'Service Quality'){
                this.paybackSer = []
            }
            if(item == 'Damage'){
                this.paybackDam = []
            }
            if(item == 'Other'){
                this.paybackOther = []
            }
            this.payback.splice(this.payback.indexOf(item), 1); 
        },
        addPaybackSer(){
            if(this.paybackSerDetials != '' && this.paybackSerPrice !=''){
                var a ={
                    itemname:this.paybackSerDetials,
                    price:this.paybackSerPrice,
                    category:'Service Quality'
                }
                this.paybackSer.push(a)
                this.paybackSerDetials = ''
                this.paybackSerPrice = ''
            }
        },
        removePaybackSer(item){
            this.paybackSer.splice(item, 1);
        },
        addPaybackOther(){
            if(this.paybackOtherDetials != '' && this.paybackOtherPrice !=''){
                var a ={
                    itemname:this.paybackOtherDetials,
                    price:this.paybackOtherPrice,
                    category:'Other'

                }
                this.paybackOther.push(a)
                this.paybackOtherDetials = ''
                this.paybackOtherPrice = ''
            }
        },
        removePaybackOther(item){
            this.paybackOther.splice(item, 1);
        },
        addPaybackDam(){
            if(this.paybackDamDetials != '' && this.paybackDamPrice !=''){
                var a ={
                    itemname:this.paybackDamDetials,
                    price:this.paybackDamPrice,
                    category:'Damage'

                }
                this.paybackDam.push(a)
                this.paybackDamDetials = ''
                this.paybackDamPrice = ''
            }
        },
        removePaybackDam(item){
            this.paybackDam.splice(item, 1);
        },
        paybackSelected(item){
            return this.payback.includes(item)
        },
        removeFromSelect(){
                if(this.damacval.length != 0){
                    for(var i = 0;i<this.damacval.length;i++){
                         this.damacval[i].selected = false
                        }
                        this.damacval[0].selected = true
                }  
        },
          selectTab(id){
              var ind = null;
              for(var i = 0;i<this.damacval.length;i++){
                  if(this.damacval[i].id == id){
                      ind = i;
                      break;
                  }
              }
              if(ind != null){
                  return this.damacval[ind].selected
              }else{
                  
                  return false
              }
              
          },
          async submitForm(){
              var flag = true;
              console.log(this.userselect)
              let fd = new FormData();
              fd.append('visit_id',$('#id_visit').val())
              fd.append('notes',this.damagenote)
              fd.append('assigned_by',$('#id_user_id').val())
              var types = '';
              for(var i = 0 ;i<this.value.length;i++){
                  types = types+this.value[i].name+',';
              }
              fd.append('ticket_types',types);
              var actiontypes = ''
              for(var i = 0 ;i<this.damacval.length;i++){
                actiontypes = actiontypes+this.damacval[i].name+',';
              }   
              fd.append('actions',actiontypes);
              for(var j = 0; j<this.images.length;j++){
                  fd.append('media',this.images[j])
              }
              if(actiontypes.includes('Assign Investigator')){
                  fd.append('secondary_investigator',this.userselect.id)
              }
              if(actiontypes.includes('Internal Report')){
                  fd.append('title',this.reporttitile);
                  fd.append('report_note',this.reportnote);
              }
              if(actiontypes.includes('Payback')){
                  var p = []
                   //Service Quality','Damage','Other'],
                   if(this.payback.includes('Service Quality')){
                    for(var j = 0 ; j<this.paybackSer.length;j++){
                      p.push(this.paybackSer[j])
                    }
                  }
                   if(this.payback.includes('Damage')){
                    for(var j = 0 ; j<this.paybackDam.length;j++){
                      p.push(this.paybackDam[j])
                     }
                    }
                    if(this.payback.includes('Other')){
                        for(var j = 0 ; j<this.paybackOther.length;j++){
                          p.push(this.paybackOther[j])
                        }
                    }
                 
                  
                  
                  for(var q =0;q<p.length;q++){
                    var pstr = ''
                    pstr = p[q].itemname+','+p[q].price+','+p[q].category
                    fd.append('paybackdiscount_items',pstr);
                  }
              }
             let result = await _post('api/ticket-submitt/',fd);

             if(result.data.success){
                 location.reload()
             }else{
                showNotification('Something went wrong','error')
             }
             
              

          },
          showCleaners(){
              $('#id_cl').click();
          },
        hideAll(){
            // console.log('g')
            // for(var i =0 ;i<this.value.length;i++){        
            //           this.value[i].selected = false;
            //   }
            //   this.ser = false
            //     this.at = false
            //     this.dam = false
            if(this.value.length == 0){
                this.ser = false
                this.at = false
                this.dam = false
               
            }else{
                    if(this.value.length == 1){
                    this.value[0].selected = true
                }else{
                    this.value[0].selected = true
                }

              if(this.value[0].id == 1){
                  this.dam =true
              }else{
                  this.at = false
                 
              }
              if(this.value[0].id == 3){
                  this.at =true
              }else{
                  this.at = false
              }
              if(this.value[0].id == 2){
                  this.ser =true
              }else{
                  this.ser = false
              }
            }
        },
          selectTickets(){
              
                    var flag = true
                    var ind;
                if(this.damacval.length != 0){
                    for(var i = 0;i<this.damacval.length;i++){
                        if(this.damacval[i].selected){
                            ind = i;
                            flag = false
                            break;
                        }
                    }
                 
                    if(flag){
                        
                    this.damacval[0].selected = true
                    }else{
                        for(var i = 0;i<this.damacval.length;i++){
                         this.damacval[i].selected = false
                        }
                        this.damacval[ind].selected = true
                        }
                }  
                
             
          },
          showDam(){
              for(var i =0 ; i<this.value.length;i++){
                  if(this.value[i].id == 1){
                      if(this.value.selected){
                          return true;
                      }
                  }
              }
              return false
          },
          removeItem(id){
            var ind
            
            for(var i = 0;i<this.damacval.length;i++){
                  
                  if(this.damacval[i].id == id){
                      ind = i;
                      break;
                  }
              }
              var a = this.damacval[ind].selected;
              this.damacval.splice(ind, 1);
                if(this.damacval.length != 0){
                    for(var i = 0;i<this.damacval.length;i++){
                    this.damacval[i].selected = false
                }
                this.damacval[0].selected = true
                }
           
            
          },
          changeSeleted(id){
              var ind
            for(var i = 0;i<this.damacval.length;i++){
                  console.log(this.damacval[i].id)
                  if(this.damacval[i].id == id){
                      ind = i;
                      break;
                  }
              }
              for(var i = 0;i<this.damacval.length;i++){
                  this.damacval[i].selected = false
              }
              this.damacval[ind].selected = true
              
              
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

        deleteImage2(imageindex) {
        this.imageData2.splice(imageindex, 1);
        },
        uploadImgToArray2(file,fileName){
            file.lastModifiedDate = Date.now();
        
        var converted_file = new File([file],  fileName,{lastModified: Date.now()});
            console.log("file size is "+converted_file.size)
            this.ImageDetails2.url = URL.createObjectURL(converted_file);
            this.ImageDetails2.file = converted_file;
            this.imageData2.push(this.ImageDetails2);
            this.images2.push(converted_file);
            this.ImageDetails2 = {
            file: "",
            url: "",
            service:""
            
            };
            console.log(this.imageData2)
        },
        async onImageFileChanged2(event) {
        console.log(event);
        console.log("orginal file size is" + event.target.files[0].size);
        console.log(this.imageData2,this.images2,"imgd");
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

            await this.uploadImgToArray2(compressedFile, event.target.files[0].name); // write your own logic
        } catch (error) {
            console.log(error);
        }
        },



      }
  });

  
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
    var dd2 = new DropDown($('#noble-gases2'));
    var dd3 = new DropDown($('#noble-gases3'));
    var dd4 = new DropDown($('#noble-gases4'));
    var dd5 = new DropDown($('#noble-gases5'));
    var dd6 = new DropDown($('#drop_id'));

    // var dd2 = new DropDown($('#other-gases'));
    $(document).click(function () {
        // close menu on document click
        $('.wrap-drop').removeClass('active');
    });
});


async function loadvisits(order_id){
    app.isOrderSelected = false
    axios.get(url+'/api/order-details/'+order_id)
                .then(function (response) {
                    console.log(response.data.visits,"vs")
                    $('#visit_drop').empty();
                    $('#id_sched').text('-- Select Order Schedule--')
                    $('.tk-order-card').hide();
                    $(response.data.visits).each(function(key,value){
                        $('#visit_drop').append('<li><a onclick="loadvisitdata('+ value.visit_id +')">'+ value.start_at +'</a></li>')
                    })

                    $('#schedule_list_id').show();
                })

}


async function loadvisitdata(visit_id){
    app.isOrderSelected = false
    axios.get(url+'/api/visit-details/'+visit_id)
                .then(function (response) {
                    console.log(response.data,"dat")
                    app.isOrderSelected = true
                    app.value = [];
                    app.damacval = []
                    app.cleaningsections = response.data.sections
                    app.edit_servicetype = response.data.servicetype
                    console.log(response.data,"lop")
                    $('#id_sched').text(response.data.start_at)
                    $('.tk-order-card').show();

                    $('#visit_blc').text(response.data.order_no);
                    $('#id_visit').val(response.data.visit_id);
                    $('#visit_customer').text(response.data.customer_name);
                    $('#visit_customer_number').text(response.data.customer_number);
                    $('#visit_servicetype').text(response.data.servicetype);
                    $('#visit_cleaningpolicy').text(response.data.cleaningpolicy);
                    $('#visit_start_at').text(response.data.start_at);
                    $('#visit_teamleader').text(response.data.team_leader);
                    $('#visit_teamleader_image').attr("src",response.data.team_leader_image);
                    $('#visit_price').text(parseFloat(response.data.amount).toFixed(3)+' '+'KD');
                    $('#visit_no_of_cleaners').text(response.data.no_of_cleaners);

                    $('#visit_team_members').empty();

                    $(response.data.members).each(function(key,value){
                        if (key == 1){
                            $('#visit_team_members').append('<img @click="showCleaners()" src="'+value.member_image+'" class="tk-img-circle">')
                        }else{
                            $('#visit_team_members').append('<img @click="showCleaners()" src="'+value.member_image+'" class="tk-img-circle" style="margin-left: -20px;">')
                        }

                    })
                    $('#visit_team_members').append('<div @click="showCleaners()" style="margin-bottom: 0px;"  class="tk-common-text2 ml-5  pointer">'+response.data.no_of_cleaners+' cleaners</div>')

                })

}

async function ticketdata(ticket_id){
    app.isOrderSelected = false
    axios.get(url+'/api/ticket-details/'+ticket_id)
                .then(function (response) {
                    console.log(response.data,"dattt")
                    
                    

                })

}
