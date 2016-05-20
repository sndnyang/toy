/**
 * Created by 80274869 on 2014-9-5.
 */

function uploadFile(file)
{

    var reader = new FileReader();

    reader.onload = function () {
        updateData(this.result);
    }

    reader.readAsText(file);
}

function uploadFiles(files)
{
    if (files.length) 
    {
        //显示
        for (var i = 0; i < files.length; i++) 
        {
            uploadFile(files[i]);
        }
    }
}
