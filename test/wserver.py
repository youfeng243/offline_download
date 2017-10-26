# coding:utf-8
import re

ss = ur"""


<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>兰州法院司法公开系统</title>
    <meta http-equiv="x-ua-compatible" content="ie=8" />
    <meta http-equiv="pragma" content="no-cache" />
    <meta http-equiv="cache-control" content="no-cache" />
    <meta http-equiv="expires" content="0" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

    <script language="javascript" src="js/jquery.js"></script>
    <script language="javascript" src="js/public.js"></script>
    <script type="text/javascript" src="ajax.js"> </script>

    <link rel="stylesheet" type="text/css" href="css/styles.css" />
    <link rel="stylesheet" type="text/css" href="css/index.css" />
    <link href="images/yjpj_style.css" rel="stylesheet" type="text/css" />
    <link href="css/pageno.css" rel="stylesheet" type="text/css" />

    <script type="text/javascript">
     $(function(){
        $(".icconts").find("a").click(function(){
            $(".icconts").find("a").removeClass("ck");
            $(this).addClass("ck");
        });
        $(".sublinks").find("a").click(function(){
            $(".sublinks").find("a").css("color", "black");
            $(this).css("color", "red");
        });

        var bodyHeight = $("body").height();
        if(0 < bodyHeight){
            parent.$("#nr_iframe").height(bodyHeight + 20);
        }

         $(".dot").hover(function(){
	        var ah= $(this).attr("needs");
//	        $("#ptitle").text("案号："+ah);
            clearTimeout(timeout);
	        $("#webFromFloat").css({position: "absolute",'top': $(this).offset().top+10,'left': $(this).offset().left+10,'z-index':999});
	        $("#webFromFloat").show();
            RunACommamd(escape(ah), "0","SetAjxx");
            $("#pbody").css("height","100%");
        },function(){
//            $("#webFromFloat").hide();
             //鼠标移出点点
            timeout = setTimeout(function (){$("#webFromFloat").hide();},500);
         });

          $("#webFromFloat").hover(function(){
            clearTimeout(timeout);
         },function(){
            timeout = setTimeout(function (){$("#webFromFloat").hide();},500);
         });
    });
    </script>
    <style>
    .fixedLayer{
            width:75px;
            height:100px;
            line-height:20px;
            background: #FFF3D0;
            border:2px solid #B4A176;
            filter: Alpha(Opacity=90);
        }
        .nr
        {

        }
        .p_writezw
        {
        	text-align:center;
        	font-size:14px;
        	color:#555;
        }
    </style>

</head>
<body>
    <form name="form1" method="post" action="publiclist.aspx?fymc=&amp;ajlb=C27383272A46EB16746AC48B10DCC2BE&amp;type=4F813CCBFE6A7793" id="form1">
<div>
<input type="hidden" name="__EVENTTARGET" id="__EVENTTARGET" value="" />
<input type="hidden" name="__EVENTARGUMENT" id="__EVENTARGUMENT" value="" />
<input type="hidden" name="__LASTFOCUS" id="__LASTFOCUS" value="" />
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwULLTIxMDA1Mjc0MDgPZBYCAgEPZBYCAgQPZBYCAgEPZBYgAgEPDxYCHgRUZXh0BQUyNDIzNmRkAgMPDxYCHwAFBDEwNTRkZAIFDw8WBh8ABQI8PB4LQ29tbWFuZE5hbWUFATMeB1Zpc2libGVnZGQCBw8PFgYfAAUBMR8BBQExHwJoZGQCCQ8PFgQfAAUDLi4uHwJoZGQCCw8PFgYfAAUBMB8BBQEwHwJoZGQCDQ8PFgYfAAUBMR8BBQExHwJnZGQCDw8PFgYfAAUBMh8BBQEyHwJnZGQCEQ8PFgYfAAUBMx8BBQEzHwJnZGQCEw8PFgYfAAUBNB8BBQE0HgdFbmFibGVkaGRkAhUPDxYEHwAFATUfAQUBNWRkAhcPDxYEHwAFATYfAQUBNmRkAhkPDxYEHwAFATcfAQUBN2RkAhsPDxYEHwAFATgfAQUBOGRkAh8PDxYEHwAFBDEwNTQfAQUEMTA1NGRkAiEPDxYEHwAFAj4+HwEFATVkZGR2jO/u7yHIcegMKJPmlhM6MqKUNw==" />
</div>

<script type="text/javascript">
//<![CDATA[
var theForm = document.forms['form1'];
if (!theForm) {
    theForm = document.form1;
}
function __doPostBack(eventTarget, eventArgument) {
    if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
        theForm.__EVENTTARGET.value = eventTarget;
        theForm.__EVENTARGUMENT.value = eventArgument;
        theForm.submit();
    }
}
//]]>
</script>


<script src="/WebResource.axd?d=yJ0lguT-iIfAGabc1WkGb9BGFGY4Z_fnFH1eIhii6a7lgzbeiDEVjSmXTp_8HmZTpiWtjgTN6IxtWOkLZ0xQj0L7M6o1&amp;t=635588912026805809" type="text/javascript"></script>

<div>

	<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="7B205B14" />
	<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="/wEWEALA8u8HAtib8t4PAv307woCi97t4AcCs8fftwsC1rO7uwcCnLfQ6Q0CnLfkxAYCnLeoswwCnLeA/QoCnLeU2AMCnLfYxgkCnLfsoQICseG3jwkCteHzjgoCzsz92Qsl91v3MwBOkgUpfIQQ7P3HDii7bQ==" />
</div>
    <input type="hidden" name="hdPageIndex" id="hdPageIndex" value="4" />
    <input type="hidden" name="hf_fymc" id="hf_fymc" />
    <input type="hidden" name="hf_ajlb" id="hf_ajlb" value="C27383272A46EB16746AC48B10DCC2BE" />
    <input type="hidden" name="hf_type" id="hf_type" value="4F813CCBFE6A7793" />
        <ul class="ilconts" style="margin-left:5px;">
            <li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4FA7F886FE53F14A52038111A184633EDA61AD56405963DB35D5873862EA5D869&bt=28C42A65F534ACA1646CC760F96133058287B0A8A21D1781F0F90208345DD63BEBCF4A961429429E8E4A7839725A34AD7B41A8A21718014635B04684FF95C8C7D9F54B38E80BF0F1&fymc=7FF82D80725A771B287251984D1B16B14CA247256CA63134&type=4F813CCBFE6A7793' target="_blank">兰州永久兴物资有限公司诉中铁二十一局集团第二工程有限公司申请保全一案</a></p><p class="pdate"><span class="dot"  needs=(2017)甘01 财保1号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E85D03FA2B696983DB430A0BACC23A966D3&bt=00429800D0BD4F6B9180A90B645F3AE2BE277C6E82F9AF6B1FEBE1448CC2D884BC0955FBED2E8A15B1736F2373404D099D31B1C6E29874FC&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">李增荣诉甘肃长颖投资开发有限公司商品房销售合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2017)甘0102 民初155号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E85DD79523D8A7D65108E1A24BDB94C156A&bt=E115E2159B37A58700E9444E9DDC8ABDD5A7DF770A1915766A45BCD2A7BCE6EB878B0E1FD0F65A0C6541B2CA10D56A0BF3345BC76A816495715F8FC957217B41&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">中国建设银行股份有限公司兰州电力支行诉郝伟申请实现担保物权一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民特43号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E85DDFE39B94DCD0A9A4CAA63B626E3B93F&bt=32905AE3B9BE6D4919E95C036ED3A65C4B0FA7AFE5656DCC1CA31C2C36ED18CE&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">吴多林诉陈学宏民间借贷纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初8054号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E85DACAFE4E03617175D6E7F07463FEDB44&bt=A7CA8FED9DEA77F116D0A406E061BFAB7EC0B2C2F6BAA6CAC84C94DE6A2D0AE3059D2839D07DCB5486E00F131B02A78B4EE48AD4B5211DA645F498C14B6C70EFF1F352CAB49A28D8&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">兰州科力顿建材有限公司诉甘肃海外工程总公司建设工程施工合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7852号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E855B6640E48796654FB9796986A5125426&bt=632916156FD5C5F123345BC2ACAEEA7AFCCCB4A6B3127C90755F2A04E6D69FFE57059A336FE61AA45F638B9CD8B9E0EFD8FB0C9A98AB71E73F3028316F7706882D31D0868854876138E6A9D6780C1D594A8742FD6EEA3CE3&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">何海兰诉路尚礼、赵蔚珍、王佳军、陈永琴、甘肃中创房地产开发公司确认合同无效纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7181号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207F5A4049967502583C3A6BFBC7D6D75D2A&bt=C962951B8B476B45737C710B3CFF555E6BCAD6033D9D8E7C8E4AD71DBAF05158&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">简斌诉唐占虎民间借贷纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初6660号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207F010EF3F15460E11FD68CDB0AC28BE5D3&bt=20410EC2665EBCB81334B82192186ECE5D2ADFC670D40BADA9D3695CE46870AF12934E34E3575763&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">李文泉诉杨雪梅、郭军承揽合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初6694号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207F9A03249B5F628C9EC143645581C4AA02&bt=774718A391D3686FAD2AA0C9D10F5DA033584398001F33AF42AB878DE03FF34A8EA872DC1AA63D0A2E30E02C6F412CFC0AC103B1BE50B7947C00804A5A6A0B78854F05D7057FAD260EADD4F088C0166FC3FABC89704278464D33790EA3E1B96F65507C76EDE1A59A&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">甘肃省再担保集团有限公司诉陈飞龙、彭运红、城关区三森美居新派格办公家具经营部、韩广平…</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初5316号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207FD18870C274A91E0EB86991336FC3B0B3&bt=DBF70D1E142ECAE71094DEB2964411C3A4A45767FE16E27A04B0AB5BDB53650E9D9DC4195325E010&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">杜建平诉张雅琴房屋租赁合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初5047号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A44AC9ED659AB357F9BC283909B3856F1C0A4FCF35BD3E0BFF829A7DDAD8688EF7&bt=CCC07A503BFA2B850908CED629C984E2379EB60F3AF0735BFECE214378618163&fymc=A32DF5E3CE6E7653E847305C6A7F94CDD90C649B0B4FACA0&type=4F813CCBFE6A7793' target="_blank">张馨尹诉张涛抚养费纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2017)甘0104 民初1号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A44AC9ED659AB357F9BC283909B3856F1C1D55E41D2067D6496FDE9ACCC254211F&bt=4F4E3A87D575987DB361CDA7E1769470916AC3C0954B44FCE224BDCACF322CE319F4DCA203AEF486&fymc=A32DF5E3CE6E7653E847305C6A7F94CDD90C649B0B4FACA0&type=4F813CCBFE6A7793' target="_blank">鲁国海诉鲁风英、鲁风山赡养费纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0104 民初1802号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4D856C10CB61F6831F589EB724477504FC77DB6C7A11E20C109B104FB70D6DE89&bt=6E595DA67C272ED12261D00C34A1D42AA7222667DBE25C8CD625F50157261F90&fymc=85BF0B4DEC0B2D87537669C0AECAA129&type=4F813CCBFE6A7793' target="_blank">赵爱鹏诉徐红武民间借贷纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0123 民初1262号 ></span>&nbsp;&nbsp;2017-01-10</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4FA7F886FE53F14A5CDABDCC8C93CCE399CDE25F176CDC4A71E15DDF3C04A7D30&bt=FBEB861A15DCAEEDFEEED83A9DC4D5135CA8604D411CFFB53DCD1B3950FFA54058090213C2E1E4C5E4426FBD4D57D8422FA396AC5AC22849&fymc=7FF82D80725A771B287251984D1B16B14CA247256CA63134&type=4F813CCBFE6A7793' target="_blank">叶兴建诉甘肃省水利水电工程局有限责任公司劳动争议一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘01 民终2879号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4FA7F886FE53F14A5CDABDCC8C93CCE3904A42877DF576BCACEDBD164F93D5656&bt=C0ED09E8A76C7B80467F5BD5A57674E7914773E6522A586A4E8C619FDE48B4D306C1EF5337A531F8194B1F963736CABF420E96D3138BB23180375A848F666A68886A479D26DB83DA574200CBC81AA6DE17385FD69ED2E72E961B350B89CA85E56B81A799E7009674&fymc=7FF82D80725A771B287251984D1B16B14CA247256CA63134&type=4F813CCBFE6A7793' target="_blank">王斌、唐雪、赵巨山、马斌、王志鹏、豆娟、王泉霖、孙毛爽诉扬州缤纷嘉年华投资发展有限公…</a></p><p class="pdate"><span class="dot"  needs=(2016)甘01 民初726号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E85F81DC92BB000FB6311B603F5972A3B49&bt=7298851562A75942CE7E40AFF0A57857EAB50BE65CA02CF613C6D5D3AD10B50120A29314C72A3AF890FA54A80A10FBACFEB8E6C03E9BAF6119D6B8F0A2D7008E76F6F441E4ACF3CC3A66DF4708EDC7DE6950D6C50D56C4ED33A980218837F23F68B5D1E9DBC7FA6DB65FA411D64FB43838B0FE54FD2A07B08CD5F96114E4BDF8&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">岳小军诉王爽成、甘肃信汇建筑安装工程有限责任公司、兰州市城关区南山路小学、兰州市城关…</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初8030号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E85EDCA39B88C1786B5D026A0E93C9677BE&bt=87A0009A9C1BEC547AFA3D23B1F368CA46DEAE0B4572BDB82C02611F8A767CCDCF863E33772B04825FA04DA7F0316F57A5353C3C02D85AC2&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">甘肃兰海商贸集团有限公司诉贾三春供用热力合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7344号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B411E5627372763E854DF13E5BA0FE529A5DC623912E844A25&bt=87A0009A9C1BEC547AFA3D23B1F368CA46DEAE0B4572BDB84FD1BC2495DF610DAAF9B2815B1767D7302CD435B2E4B7172D5E07AE85F2512D&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">甘肃兰海商贸集团有限公司诉文立英供用热力合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7340号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207FFAC8CF43E11C0D932A0350F9A6CC5A79&bt=90F1225366BB7C7AE834F730F8B81ECA21A770518E519332817BFF7CE0FEC4248C582F95088D629B6578216BB3386E1BDD87BCCC42815EA9&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">兰州碧桂园房地产开发有限公司诉简波房屋买卖合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7026号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207FA63877C4C43048C067260E3BC75C2378&bt=E5639DC88549960416C79CEDCDB44CE8019945D4F783FBD16AF6561D263B3F6E&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">徐金花诉肖首星民间借贷纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7015号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207F87A27985FAFB1500629776F3F4E59B42&bt=2CE46BF3E45A1189096B045320D69B5F0DD9EBFBB98702E36446CB37147586DD&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">王新萍诉刘会连民间借贷纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7014号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207F8D4EA8CFEF7FB1D8982FFC8E865E5C8D&bt=4EC6F5FAB5F2F4E06BB409462E86A8CC8B5C6BAB171AD8816AE3128303A78EA4AA1996C1E01AA811DB906273F6649B15&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">兰州大学出版社有限责任公司诉韩庆利合同纠纷一案</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初7012号 ></span>&nbsp;&nbsp;2017-01-09</p></li><li class="datas"><p class="ptitle"> <a href=' cpwsplay.aspx?cpws=A68E8B2F352BD61D71EC04E9B55A12A4CB62314A9F42D9B4E8869F4FDD82207F8CC099EF389E1E6BB39876015F3702CF&bt=8CEB458D1949CD56EB4363D7F826E74D786529AA49BC6001EF7295C1919A5A488C4E2754FC0C6F8D9011C0A7F89F61AA8D5FEE07951E52D74FD9B5126FB69ED74F99DB49489A71E8E81AE89D21145921F1A925D37D55280FB832B384C15C008FE787B5D2A9EBA61506C0C1AA717DE93C5A9CF24A8C3F356D&fymc=F9194A6DF9D02FCA02916E70B7CE44204E958AEC2EE9C547&type=4F813CCBFE6A7793' target="_blank">解振亚诉中国太平洋财产保险股份有限公司兰州中心支公司、兰州自来水工程设计事务所、崔海…</a></p><p class="pdate"><span class="dot"  needs=(2016)甘0102 民初6723号 ></span>&nbsp;&nbsp;2017-01-09</p></li>
            <li class="pageinfo">
                <div class="page">
                    <div id="plPageInfo">

                        <div id="pageno">
                            <table width="90%" border="0" cellspacing="0" cellpadding="0">
                                <tr>
                                    <td width="100%" height="30" align="center" valign="middle">
                                        <div id="plPages">

                                            <span class="page-txt">共&nbsp;
                                                <span id="lbTotalCount">24236</span>
                                                &nbsp;条， 共&nbsp;
                                                <span id="lbPageCount">1054</span>
                                                &nbsp;页&nbsp; </span><span class="page-other">
                                                    <a id="btnPrev" title="上一页" href="javascript:__doPostBack('btnPrev','')"><<</a>
                                                </span><span class="page-other">

                                                </span>

                                            <span class="page-other">

                                            </span><span class="page-other">
                                                <a id="btnPage2" href="javascript:__doPostBack('btnPage2','')">1</a>
                                            </span><span class="page-other">
                                                <a id="btnPage3" href="javascript:__doPostBack('btnPage3','')">2</a>
                                            </span><span class="page-other">
                                                <a id="btnPage4" href="javascript:__doPostBack('btnPage4','')">3</a>
                                            </span><span class="page-cur">
                                                <a id="btnPage5" disabled="disabled">4</a>
                                            </span><span class="page-other">
                                                <a id="btnPage6" href="javascript:__doPostBack('btnPage6','')">5</a>
                                            </span><span class="page-other">
                                                <a id="btnPage7" href="javascript:__doPostBack('btnPage7','')">6</a>
                                            </span><span class="page-other">
                                                <a id="btnPage8" href="javascript:__doPostBack('btnPage8','')">7</a>
                                            </span><span class="page-other">
                                                <a id="btnPage9" href="javascript:__doPostBack('btnPage9','')">8</a>
                                            </span>
                                            <span id="lbLast">...</span>
                                            <span class="page-other">
                                                <a id="btnLast" title="最后一页" href="javascript:__doPostBack('btnLast','')">1054</a>
                                            </span><span class="page-other">
                                                <a id="btnNext" title="下一页" href="javascript:__doPostBack('btnNext','')">>></a>
                                            </span><span class="page-txt">&nbsp;到第
                                                <input name="tbGoPage" type="text" maxlength="5" onchange="javascript:setTimeout('__doPostBack(\'tbGoPage\',\'\')', 0)" onkeypress="if (WebForm_TextBoxKeyHandler(event) == false) return false;" id="tbGoPage" onkeydown="JavaScript:CheckInputForNaturalNumber(this);" style="width:26px;" />
                                                页 </span>

	</div>
                                    </td>
                                </tr>
                            </table>
                        </div>

</div>
                </div>
            </li>
        </ul>





   <div id="webFromFloat" class="fixedLayer" style="display:none;">
       <div id="web_xs" class="nr" >
          <div><p id="ptitle"></p></div>

          <div id=pbody></div>
       </div>
   </div>
    </form>
</body>
</html>
"""

view_state_regx = re.compile("""<input.*?"__VIEWSTATE".*?value="(.*?)".*?/>|<input.*?value="(.*?)".*?"__VIEWSTATE".*?/>""")
print "".join(view_state_regx.findall(ss)[0])