const app = new Vue({
    el: "#app",
    
    delimiters: ["<%", "%>"],
    
    mounted() {

    },
   
    data: {
        url:'http://localhost:8000',
        userid:'',
        order_id:'',
        service_books:[],
        

    },
    methods:{
        doCancellation(){
            axios.post(this.url+'/customer/service/cancell/',
            {cancelled_by:this.userid,
            order_id:this.order_id,
            service_books:this.service_books
            }
            )
        }
    },

})