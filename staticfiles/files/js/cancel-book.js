


const app = new Vue({
    el: "#app",
    
    delimiters: ["<%", "%>"],
    
    mounted() {
        this.url = api;

    },
   
    data: {
    url:'',
        user_id:'',
        order_id:'',
        service_books:[],
        services:[],
        details:{
            id:'',
            amount:'',
            action_type:''
        }
      
        

    },
    methods:{
        setDetails(){

        },
        doCancellation(return_url){
            axios.post(this.url+'/customer/service/cancell/',
            {cancelled_by:this.user_id,
            order_id:this.order_id,
            service_books:this.service_books
            }
            
            ).then(response=>{
                //location.href="/bleach_salesadmin/dashboard/"
                location.href=return_url
            })
        },
        setData(returnurl){
            for(var i=0;i<this.services.length;i++){

                var action_type=$('#cancel_method_id-'+this.services[i].id).val()
                this.service_books.push({
                  id:this.services[i].id,
                  action_type:action_type,
                  amount:this.services[i].amount  
                })
            }
            this.doCancellation(returnurl)
        }
    },

})
function submitCancel(service,rurl){
    app.user_id=$(service).data('user_id')
    app.order_id=$(service).data('order_id')
   
    app.setData(rurl)

}