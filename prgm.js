 function check(){
            let name=document.getElementById("name").value;
            let number=document.getElementById("number").value;
            let gender=document.getElementById("gender").value;
            if(name===""&&number===""&&gender===""){
                alert("please fill required fields");
            }
            else if(name==="")
            {
                alert("name must be filled out");
                return false;
            }
             else if(number==="")
            {
                alert("number must be filled out");
                return false;
            }
             else if(gender===""||gender==="select")
            {
                alert("gender must be filled out");
                return false;
            }
            else{
                document.write("data saved successfully");
            }
        }