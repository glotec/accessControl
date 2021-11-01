function triggerClick()
{
    document.querySelector('#profileImage').click();
}

function displayImage(e)
{
    if (e.files[0])
    {
        var reader = new FileReader();

        reader.onload = function (e)
        {
            document.querySelector('#profileDisplay').setAttribute('src', e.target.result);
        }
        reader.readAsDataURL(e.files[0]);
    }
}

// validate imagee upload
$(document).ready(function() {
//File type validation
$("#fileInput").change(function() {
    var fileLength = this.files.length;
    var match = ["image/jpeg", "image/jpg", "image/png"]
    var i;
    for (i = 0; i < fileLength; i++) {
        var file = this.files[i];
        var imagefile = file.type;
        if(!((imagefile==match[0]) || (imagefile==match[1]) || (imagefile==match[2]) || (imagefile==match[3]))) {
            alert('Veillez choisir une photo (JPEG, PNG, JPG).')
            $("#fileInput").val('');
            return false;
        }
    }
});
});