The XML file in which are recorded the sha1sum of the followed files is of the form 


+++++++++++++++++++++++++++++++++++++++++
<?xml version="1.0" ?>
<Followed_files>
	<fichier name="ess.py" sha1sum="a329313819092a183ca8b08bb7c178807a1a68b7"/>
	<fichier name="ess.aux" sha1sum="be730c54ff1d1a75398a496283efe45c675dc54f"/>
</Followed_files>
+++++++++++++++++++++++++++++++++++++++++++


The principal XML object is got by
root = minidom.parse(<filename>)

Then the «list of lists» of elements "Followed_files" is got by
fileNodes = root.getElementsByTagName("Followed_files")

In the example above, there is only one. At this point fileNodes is a list whole element 0 represents the lines
	<fichier name="ess.py" sha1sum="a329313819092a183ca8b08bb7c178807a1a68b7"/>
	<fichier name="ess.aux" sha1sum="be730c54ff1d1a75398a496283efe45c675dc54f"/>

Each element in these lines has the tag "fichier". Then the list is given by
fileNode.getElementsByTagName("fichier")

The first element of that list represents the line
	<fichier name="ess.py" sha1sum="a329313819092a183ca8b08bb7c178807a1a68b7"/>

If F = fileNode.getElementsByTagName("fichier")[0], then we get the name by
F.getAttribute("sha1sum")


