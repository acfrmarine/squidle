<table background-color="#111" class="table table-striped table-condensed">
<tr height="73" background-color="#111">
<#list features as feature>
    <td width="98"><a href="javascript:launchImageModal(${feature.id.value})"><img src="/media/catami_live/importedimages/${feature.web_location.value}" width="73" height="98"/></td>
</#list>	
</tr>
<tr>
<#list features as feature>
<td><div style="font-size:10px;"><strong>Depth:</strong>${feature.depth.value}</div></td>
</#list>
</tr>
<tr>
<#list features as feature>
<td><div style="font-size:10px;"><strong>Lat:</strong>${feature.position.rawValue[7..13]}</div></td>
</#list>
</tr>
<tr>
<#list features as feature>
<td><div style="font-size:10px;"><strong>Long:</strong>${feature.position.rawValue[19..25]}</div></td>
</#list>
</tr>
</table>

<!-- Modal -->
<div id="myModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
<div class="modal-header">
<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
<h3 id="myModalLabel">Modal header</h3>
</div>
<div class="modal-body">
<p>One fine body…</p>
</div>
<div class="modal-footer">
<button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
<button class="btn btn-primary">Save changes</button>
</div>
</div>
