let app = new Vue({
    el: "#app",
    components: { Multiselect: window.VueMultiselect.default },
    delimiters: ["<%", "%>"],
    mounted(){
      this.getKitchen()
    },
    computed: {
     
      totalAmount: function () {
        var sum =0;
        for(var i = 0 ; i<this.cleaningsections.length;i++){
          sum = sum + parseInt(this.cleaningsections[i].section_net_cost);
        }
        
        return sum;
      }
    },
    data () {
          return {
            loading:false,
            isSelectedSolt:false,
            checkVer:false,
            functionClick:0,
            is_agent_checked:false,
            durationArray:[2,4,8,10],
            avSolt:null,
            incheck:false,
            incheck2:false,
            sofa_size:[],
            chair_size:[],
            new_kitchen_cabinet_size:[],
            old_kitchen_cabinet_size:[],
            new_kitchen_nocabinet_size:[],
            old_kitchen_nocabinet_size:[],
            newkeynote:{
              sub_area:'',
              quantity:''
            },
            keynote_msg:false,
            service_productivity:[],
            sizeSelect:'',
            productivity:{},
            sectionfull:null,
            cleaning_hours:null,
            noofcleaners:'',
            totalcost:'',
            cause_of_stain:['INK MARK', 'HARD DUST', 'COFFEE & TEA SPILL', 'OIL','GREASE', 'PAINT', 'URINE', 'MILK SPILL', 'NO STAIN', 'OTHERS'],
            walltypes:["BRICKS","GLASS","CONCRETE","CERAMIC","GYPSUM","FABRIC","RUBBER","STONE","TERRAZO","STAINLESS","VINYL","WOODEN","OTHERS"],
            ceilingtypes:["WOODEN","GLASS","CONCRETE","CERAMIC","GYPSUM","FOAM","PLASTIC","FABRIC","RUBBER","STAINLESS","VENYL","OTHERS"],
            floortypes:["MARBLE","GLASS","STONE","CERAMIC","CONCRETE","BRICKS","WOODEN","TERRAZO","OTHERS"],
            materials:["POLYESTER","NATURAL FIBER","SYNTHETIC","LEATHER","OLEFIN","POLYPROPYLENE","NYLON"],
            colors:["GREEN","SILVER","VIOLET","WHITE","BLACK","BEIGE","BLUE","GREY","RED","CREAM","MULTI","OFF WHITE","MEROON","ORANGE","PINK","GOLD","BROWN","YELLOW","ROYAL BLUE","LILAC","OTHERS"],
            tentdate:'',
            tenttime:'',
            soltselected:false,
            notes:'',
            visitid:'',
            editSectionData:{
              is_highprice_window:null,
              age_of_stain:'',
              size:'',
              keynotes:[],
              section_cost:0,
              section_name:'',
              floor_type:[],
              ceiling_type:[],
              wall_type:[],
              material:[],
              color:[],
              cause_of_stain:[],
              category:'Floor',
              age:null,
              new_kitchen:null,
              is_cabinet:null,
              oil_residue:null
             },
            edit_section_active_index:null,
            service_type:'',
            cleaningsections:[],
            selectedDate: new Date(),
              addfollow:false,
            imageData: [],
            images:[],
            ImageDetails: {
                url: "",
                file: "",
                service:""
            },
            render:true,
            highprice_window:[],
            lowprice_window:[],
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
    watch: {
      selectedDate: function() {
        this.selected_slots = [];
          this.getAvalibility();


      }
  },
    methods:{
      getTotal(){
        var sum =0;
        for(var i = 0 ; i<this.cleaningsections.length;i++){
          console.log(this.cleaningsections[i].section_net_cost,'xot')
          sum = sum + parseInt(this.cleaningsections[i].section_net_cost);
        }
        
        return sum;
      },
      inputEvents(){
        console.log("date chaneg")
      },
      checkAgentSub(){
        this.isSelectedSolt = false;
        this.checkVer = false
        if(this.tenttime ==''){
          this.isSelectedSolt = true;
        }else{
          this.submitAgentForm()
        }
        
      },
      chechIsver(){
        this.checkVer = false
        if(!this.is_agent_checked){
          this.checkVer = true
        }
      },
      async submitAgentForm(){

         let fd = new FormData();
         fd.append('investigation_id',this.visitid);
         
        fd.append('tendative_date',this.tentdate);
        fd.append('tendative_time',this.tenttime);
        fd.append('is_agent_checked',true)
        this.loading = true
         let result = await _post('api/agent-investigation-check/',fd);
         
         if(result.data.success){
           console.log("success")
           window.location.href = '../../dashboard'
         }else{
          this.loading  = false
           showNotification('Something went wrong','error')
         }
         console.log(result)


       },
      checkAvalSolt(index){
        var tempIndex = index*2;
        if(this.avSolt != null){
          if(this.avSolt[tempIndex].length == 0){
            return false
          }else{
            return true
          }
        }else{   
          return true
        }
      },
      async getAvalibility(){
        
        this.avSolt = null;
        
        let result = await _post("customer/ajax/getmultipleservicecleaningslotes",{
          cleaning_date:moment(this.selectedDate).format('DD-MM-YYYY'),
          number_of_cleaners:this.noofcleaners,
          service_types:[this.service_type]
        })
        this.avSolt = result.data.slotes
        console.log(this.avSolt)
      },
      openSoltModal(){
        this.incheck = false
        if(this.noofcleaners == ''){
          this.incheck = true
        }else{
          
          this.getAvalibility();
          $("#id_modal_btn").click();
        }
      
      },
      resetWindowSize(){
        this.editSectionData.size={}
        this.calcSectionCost()
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
          this.editSectionData.section_cost=this.editSectionData.size*this.sofa_size[0].unit_price;
       }
        

      },
      resetKitchenSize(){
        this.editSectionData.size={}
        this.calcSectionCost();
      },
      
      formatKitchenSize(){
        this.new_kitchen_cabinet_size = []
        this.old_kitchen_cabinet_size = []
        this.new_kitchen_nocabinet_size = []
        this.old_kitchen_nocabinet_size =[]
        for(var i=0;i<this.service_productivity.length;i++){
          if(this.service_productivity[i].is_newkitchen){
            if(this.service_productivity[i].is_cabinet){
              this.new_kitchen_cabinet_size.push(this.service_productivity[i])
            }else{
              this.new_kitchen_nocabinet_size.push(this.service_productivity[i])
            }
         
          }
          else{
            if(this.service_productivity[i].is_cabinet){
             this.old_kitchen_cabinet_size.push(this.service_productivity[i])
            }
            else{
              this.old_kitchen_nocabinet_size.push(this.service_productivity[i])
            }
          }
        }
        var size = this.cleaningsections[this.edit_section_active_index].size;
        var cab = this.cleaningsections[this.edit_section_active_index].is_cabinet;
        var isnew = this.cleaningsections[this.edit_section_active_index].new_kitchen;
        for(var i =0;i<this.service_productivity.length; i++){
          if(this.service_productivity[i].name == size && this.service_productivity[i].is_cabinet == cab && this.service_productivity[i].is_newkitchen == isnew){
            this.editSectionData.size = this.service_productivity[i];
            break;
          }
        }


      },
      addToKeynote(){
        if(this.newkeynote.sub_area && this.newkeynote.quantity)
        {
          this.editSectionData.keynotes.push(this.newkeynote);
          this.newkeynote={
            sub_area:'',
            quantity:''
          }
        }
        else{
          this.keynote_msg=true
        }
      },
      delKeynote(index){
        console.log(index)
        this.editSectionData.keynotes.splice(index,1)
      },
      calcSectionCost(){
        this.editSectionData.section_cost = this.editSectionData.size.cost || 0;
      },
      formatWindowSize(){
        this.highprice_window=[]
        this.lowprice_window=[]
        for(var i=0;i<this.service_productivity.length;i++){
          if(this.service_productivity[i].is_highprice_window){
            this.highprice_window.push(this.service_productivity[i])
          }
          else{
            this.lowprice_window.push(this.service_productivity[i])
          }
        }
        var size = this.cleaningsections[this.edit_section_active_index].size;
        var w = this.cleaningsections[this.edit_section_active_index].is_highprice_window;
        for(var i=0;i<this.service_productivity.length;i++){
          if(this.service_productivity[i].name == size && this.service_productivity[i].is_highprice_window == w){
            this.editSectionData.size = this.service_productivity[i];
            break;
          }
        }
      },
      async getKitchen(){
        let result = await _get('customer/ajax/getservicesizeprice?service_type=Kitchen Cleaning');
        var productivity = result.data;
        var  service_productivity = []
        for(var i in productivity){
          productivity[i].combined_size=productivity[i].name+' ( '+productivity[i].min_size+' sq.m - '+productivity[i].max_size+' sq.m )'
          service_productivity.push(productivity[i])
        }
        this.new_kitchen_cabinet_size = []
        this.old_kitchen_cabinet_size = []
        this.new_kitchen_nocabinet_size = []
        this.old_kitchen_nocabinet_size =[]
        for(var i=0;i<service_productivity.length;i++){
          if(service_productivity[i].is_newkitchen){
            if(service_productivity[i].is_cabinet){
              this.new_kitchen_cabinet_size.push(service_productivity[i])
            }else{
              this.new_kitchen_nocabinet_size.push(service_productivity[i])
            }
         
          }
          else{
            if(service_productivity[i].is_cabinet){
             this.old_kitchen_cabinet_size.push(service_productivity[i])
            }
            else{
              this.old_kitchen_nocabinet_size.push(service_productivity[i])
            }
          }
        }
        
      },
      async getSize(type){
        // if(type=='Hourly Cleaning'){
        //   type='General Cleaning'
        // }
        // this.service_productivity = [];
        // let result = await _get('customer/ajax/getservicesizeprice?service_type='+type);
        // console.log(result)
        // this.productivity=result.data
        //   for(var i in this.productivity){
        //     this.productivity[i].combined_size=this.productivity[i].name+' ( '+this.productivity[i].min_size+' sq.m - '+this.productivity[i].max_size+' sq.m )'
        //     this.service_productivity.push(this.productivity[i])
        //   }
        //   var size = this.cleaningsections[this.edit_section_active_index].size;
        //   if(this.service_type=='Kitchen Cleaning'){
        //     this.formatKitchenSize()
        //   }else if(this.service_type=='Upholstery Cleaning'){
        //     this.chair_size = [];
        //     this.sofa_size = [];
        //     for(var i=0;i<this.service_productivity.length;i++){
        //       if(this.service_productivity[i].upholstery_type == "CHAIR"){
        //         this.chair_size.push(this.service_productivity[i]);
        //       }
        //       if(this.service_productivity[i].upholstery_type == "SOFA"){
        //         console.log('sofa push')
        //         this.sofa_size.push(this.service_productivity[i]);
        //       }
        //     }
        //     if(this.editSectionData.upholstery_type == 'CHAIR'){
        //       for(var i =0;i<this.chair_size.length; i++){
        //         if(this.chair_size[i].name == size){
        //           this.editSectionData.size = this.chair_size[i];
        //           break;
        //         }
        //       }

        //     }else if(this.editSectionData.upholstery_type == 'SOFA'){
        //       this.editSectionData.size = size.split(" ")[0];
        //     }

        //   }else if(this.service_type=='Window Cleaning'){
        //     this.formatWindowSize();
        //   }else{
        //     for(var i =0;i<this.service_productivity.length; i++){
        //       if(this.service_productivity[i].name == size){
        //         this.editSectionData.size = this.service_productivity[i];
        //         break;
        //       }
        //     }

        //   }

          
      },
      editSection(item){
        if(this.service_type == 'Upholstery Cleaning'){
          this.editSectionData.upholstery_type = this.cleaningsections[item].upholstery_type
        }
        this.edit_section_active_index = item
        //this.getSize(this.service_type)
        this.editSectionData.size = this.cleaningsections[item].size
        
        this.editSectionData.section_name = this.cleaningsections[item].section_name
        this.editSectionData.age = this.cleaningsections[item].age

        this.editSectionData.section_cost = this.cleaningsections[item].section_net_cost
        this.editSectionData.keynotes = this.cleaningsections[item].keynotes
        this.editSectionData.oil_residue = this.cleaningsections[item].oil_residue
        this.editSectionData.is_cabinet = this.cleaningsections[item].is_cabinet
        this.editSectionData.new_kitchen = this.cleaningsections[item].new_kitchen
        this.editSectionData.age_of_stain = this.cleaningsections[item].age_of_stain
        this.editSectionData.is_highprice_window = this.cleaningsections[item].is_highprice_window



        if(this.cleaningsections[item].wall_type != null){
          this.editSectionData.wall_type = this.cleaningsections[item].wall_type.split(",");
        }
        if(this.cleaningsections[item].floor_type != null){
          this.editSectionData.floor_type = this.cleaningsections[item].floor_type.split(",");
        }
        if(this.cleaningsections[item].ceiling_type != null){
          this.editSectionData.ceiling_type = this.cleaningsections[item].ceiling_type.split(",");
        }
        if(this.cleaningsections[item].material != null){
          this.editSectionData.material = this.cleaningsections[item].material.split(",");
        }
        if(this.cleaningsections[item].color != null){
          this.editSectionData.color = this.cleaningsections[item].color.split(",");
        }    
        if(this.cleaningsections[item].cause_of_stain != null){
          if(this.cleaningsections[item].cause_of_stain != ''){
            this.editSectionData.cause_of_stain = this.cleaningsections[item].cause_of_stain.split(",");
          }else{
            this.editSectionData.cause_of_stain = []
          }
          
         
        }        
        $('#edit-dialog-tigger').click();
    },
      saveEdit(){
        this.cleaningsections[this.edit_section_active_index].section_name = this.editSectionData.section_name;
        this.cleaningsections[this.edit_section_active_index].age = this.editSectionData.age;
        // if(this.service_type =='Upholstery Cleaning'){
        //   if(this.editSectionData.upholstery_type == 'CHAIR'){
        //     this.cleaningsections[this.edit_section_active_index].size = this.editSectionData.size.name;
        //   }
        //   if(this.editSectionData.upholstery_type == 'SOFA'){
        //     this.cleaningsections[this.edit_section_active_index].size = this.editSectionData.size + ' Seater';
        //   }

        // }else{
        //   this.cleaningsections[this.edit_section_active_index].size = this.editSectionData.size.name;
        // }
        this.cleaningsections[this.edit_section_active_index].size = this.editSectionData.size;

        this.cleaningsections[this.edit_section_active_index].keynotes = this.editSectionData.keynotes;
        this.cleaningsections[this.edit_section_active_index].section_net_cost = this.editSectionData.section_cost;
        this.cleaningsections[this.edit_section_active_index].wall_type = this.editSectionData.wall_type.toString();
        this.cleaningsections[this.edit_section_active_index].floor_type = this.editSectionData.floor_type.toString();
        this.cleaningsections[this.edit_section_active_index].ceiling_type = this.editSectionData.ceiling_type.toString();
        this.cleaningsections[this.edit_section_active_index].material = this.editSectionData.material.toString();
        this.cleaningsections[this.edit_section_active_index].color = this.editSectionData.color.toString();
        this.cleaningsections[this.edit_section_active_index].cause_of_stain = this.editSectionData.cause_of_stain.toString();
        this.cleaningsections[this.edit_section_active_index].age_of_stain =  this.editSectionData.age_of_stain
        this.cleaningsections[this.edit_section_active_index].oil_residue =  this.editSectionData.oil_residue
        this.cleaningsections[this.edit_section_active_index].is_cabinet =  this.editSectionData.is_cabinet
        this.cleaningsections[this.edit_section_active_index].new_kitchen =  this.editSectionData.new_kitchen
        this.cleaningsections[this.edit_section_active_index].is_highprice_window =  this.editSectionData.is_highprice_window



        $('#id_model_edit_close').click();
      },
      deleteSection(index){
        if(this.cleaningsections.length>1){
          this.cleaningsections.splice(index,1)
        }
        
      },
      confirmSolt(){
        if(this.selected_slots.length !=0){
          console.log(this.selected_slots)
          this.tentdate = moment(this.selectedDate).format('DD-MM-YYYY');
          var a = Math.min(...this.selected_slots);
         
         
          this.tenttime = this.time_slots[a].start_time;
          this.soltselected = true;
          this.cleaning_hours = this.selected_slots.length * 2;
          $('#id_model_close').click();

        }
      },
      confirmSolt2(){
        if(this.selected_slots.length !=0){
          console.log(this.selected_slots)
          this.tentdate = moment(this.selectedDate).format('DD-MM-YYYY');
          var a = Math.min(...this.selected_slots);
         
         
          this.tenttime = this.time_slots[a].start_time;
          this.soltselected = true;
          
          $('#id_model_close').click();

        }
      },
      clearsoltSelection(){
        this.selected_slots= [];
        this.selectedDate = new Date();
      },
        disableSolt(item){

          if(this.selected_slots.length != 0 ){
            if(this.selected_slots.includes(item)){
              return false
            }else{
              var a = this.selected_slots.includes(item-1);
              var b = this.selected_slots.includes(item+1);
              if(a || b){
                return false
              }else{
                return true
              }

            }
            
          }else{
            return false
          }

        },
       
        removeSelected(item){
            var index = this.selected_slots.indexOf(item);
            if (index !== -1) {
                var temp = this.selected_slots.length;
                for(var i =0; i <temp;i++){
                  console.log(this.selected_slots[i],item)
                  if(this.selected_slots[i]>item){
                    this.selected_slots.splice(i, 1);
                  }
                 
                }
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
        async makeSectionFull(){
          console.log('string')
          var a = '';

          for(var i = 0 ; i<this.cleaningsections.length;i++){
            var tempkeynote=''
            console.log(this.cleaningsections[i]);
            for(var j = 0 ; j<this.cleaningsections[i].keynotes.length;j++){
              tempkeynote = tempkeynote+ "{'keynote':"+this.cleaningsections[i].keynotes[j].sub_area+",'quantity':"+this.cleaningsections[i].keynotes[j].quantity+"},"
            }
            
            a = a + "{'section_name':"+this.cleaningsections[i].section_name+", 'size':"+this.cleaningsections[i].size+", 'wall_type':"+this.cleaningsections[i].wall_type+", 'ceiling_type':"+this.cleaningsections[i].ceiling_type+", 'floor_type':"+this.cleaningsections[i].floor_type+", 'section_cost':"+this.cleaningsections[i].section_net_cost+",keynotes:["+tempkeynote+"]},"
          
          }

          this.sectionfull  = '['+a+']';
          console.log(this.sectionfull)

        },

        changeCheckBox(){
          if(this.functionClick % 2 ==  0){
          this.is_agent_checked = !this.is_agent_checked
          }
          this.functionClick = this.functionClick+1
        },
        checkValidation(){
          if(this.addfollow){
            var flag = true
          this.incheck = false
          this.incheck2 = false

          if(this.noofcleaners == ''){
            this.incheck = true
            flag = false
          }
          if(this.cleaning_hours == null){
            this.incheck2 = true
            flag = false
          }
          if(flag){
            this.submitForm();
          }

          }else{
            this.submitForm();

          }
          
        },
        async submitForm(){
         var tempSections = JSON.stringify(this.cleaningsections);
         

          console.log(this.visitid)
          let fd = new FormData();
          fd.append('investigation_id',this.visitid);
          fd.append('notes',this.notes);
          for(var j = 0; j<this.images.length;j++){
            fd.append('media',this.images[j])
          }
          if(this.addfollow){
            console.log(this.sectionfull,"sefull")
            await this.makeSectionFull();
            fd.append('is_followup','True');
            fd.append('number_of_cleaners',this.noofcleaners);
            fd.append('total_cost',this.totalAmount);
            // fd.append('tendative_date',this.tentdate);
            // fd.append('tendative_time',this.tenttime);
            fd.append('cleaning_hours',this.cleaning_hours);
            fd.append('sections',tempSections);

          }else{
            fd.append('is_followup','False');

          }
          this.loading = true
          let result = await _post('api/investigation-form/',fd);
          
          if(result.data.success){
            console.log("success")
              window.history.back()
              // window.location.href = url+'/stl/dashboard'
            
          }else{
            this.loading = false
            showNotification('Something went wrong','error')
          }
          console.log(result)


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