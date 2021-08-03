


const app = new Vue({
    el: "#app",
    
    delimiters: ["<%", "%>"],
    
    mounted() {

    },
   
    data: {
        url:'http://localhost:8000',
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
        doCancellation(){
            axios.post(this.url+'/customer/service/cancell/',
            {cancelled_by:this.user_id,
            order_id:this.order_id,
            service_books:this.service_books
            }
            )
        },
        setData(){
            for(var i=0;i<this.services.length;i++){

                var action_type=$('#cancel_method_id-'+this.services[i].id).val()
                this.service_books.push({
                  id:this.services[i].id,
                  action_type:action_type,
                  amount:this.services[i].amount  
                })
            }
            this.doCancellation()
        }
    },

})
function submitCancel(service){
    app.user_id=$(service).data('user_id')
    app.order_id=$(service).data('order_id')
   
    app.setData()

}