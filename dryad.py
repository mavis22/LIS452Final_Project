from lxml import etree
from io import BytesIO
import glob

#Dealing with header
def get_record(file_in):
    f=open(file_in,'r')
    xml_string=f.read()
    end=xml_string.find('</header>')
    result=xml_string[:end+9]
    return result

xml_files=glob.glob('dryad/*.xml') #Enter the path of folder here
for file_path in xml_files:
    tree = etree.parse(file_path)
    root = tree.getroot()
    document_id = file_path.split('/')[-1]
    document_id=document_id.split('.')[0]
    fout=open(document_id+'_dublincore.xml','wb')
    ns = {'xmlns': 'http://datacite.org/schema/kernel-2.2'}

    #extract information
    identifier=root.xpath("//xmlns:identifier/text()",namespaces=ns)
    identifierType=root.xpath("//xmlns:identifier/@identifierType",namespaces=ns)

    creator_results=[]
    creators=root.xpath("//xmlns:creators/xmlns:creator",namespaces=ns)
    for creator in creators:
        creatorName=creator.xpath("xmlns:creatorName/text()",namespaces=ns)
        creator_results.append(creatorName[0])

    title_results=[]
    titles=root.xpath("//xmlns:titles",namespaces=ns)
    for title in titles:
        titleName=title.xpath("xmlns:title/text()",namespaces=ns)
        title_results.append(titleName[0])

    publisher=root.xpath("//xmlns:publisher/text()",namespaces=ns)
    publicationYear=root.xpath("//xmlns:publicationYear/text()",namespaces=ns)

    subject_results=[]
    subjects=root.xpath("//xmlns:subjects",namespaces=ns)
    for subject in subjects:
        subjectName=subject.xpath("xmlns:subject/text()",namespaces=ns)
        subject_results.append(subjectName[0])

    #datetype=root.xpath("//xmlns:dates/xmlns:date/@dateType",namespaces=ns)
    date_accepted=root.xpath("//xmlns:dates/xmlns:date[@dateType='Accepted']/text()",namespaces=ns)
    resourcetype=root.xpath("//xmlns:resourceType/text()",namespaces=ns)
    resourcetypegeneral=root.xpath("//xmlns:resourceType/@resourceTypeGeneral",namespaces=ns)



    rel_identifiers=root.xpath("//xmlns:relatedIdentifiers/xmlns:relatedIdentifier", namespaces=ns)
    rel_iden_results=[]
    for each in rel_identifiers:
       rel_type=each.xpath("@relationType",namespaces=ns)
       rel_iden_type=each.xpath("@relatedIdentifierType",namespaces=ns)
       rel_iden=each.xpath("text()",namespaces=ns)
       if rel_iden==[]:
           rel_iden='NA'
       else:
           rel_iden=rel_iden[0]
       sub_result=[rel_type[0],rel_iden_type[0],rel_iden]
       rel_iden_results.append(sub_result)

    alt_iden_type=root.xpath("//xmlns:alternateIdentifiers/xmlns:alternateIdentifier/@alternateIdentifierType",namespaces=ns)
    alt_iden=root.xpath("//xmlns:alternateIdentifiers/xmlns:alternateIdentifier/text()",namespaces=ns)
    if len(alt_iden_type) is not 0:
            testout.write(document_id+" ")
            testout.write(alt_iden_type[0]+'\n')

    size=root.xpath("//xmlns:sizes/xmlns:size/text()",namespaces=ns)

    right=root.xpath("//xmlns:rights/text()",namespaces=ns)

    des_type=root.xpath("//xmlns:descriptions/xmlns:description/@descriptionType",namespaces=ns)
    des=root.xpath("//xmlns:descriptions/xmlns:description/text()",namespaces=ns)
    if len(des) is 0:
       des=''
    else:
       des=des[0]

    # Start to transform into Dublin Core
    #<record> part, no change
    record=etree.XML(get_record(file_path)+"</record>")
    #<metadata> part, for Dublin Core
    oai_dc=etree.XML("""<oai_dc:dc
       xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/"
       xmlns:dc="http://purl.org/dc/elements/1.1/"
       xmlns:dcterms="http://purl.org/dc/terms/"
       xmlns:dcmitype="http://purl.org/dc/dcmitype/"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">"""+"</oai_dc:dc>")
    metadata=etree.SubElement(record,"metadata")
    metadata.append(oai_dc)
    dc = "http://purl.org/dc/elements/1.1/"
    dcterms="http://purl.org/dc/terms/"
    xsi="http://www.w3.org/2001/XMLSchema-instance"
    dcmitype="http://purl.org/dc/dcmitype/"

    #Informaiton part
    if len(identifier) is not 0:
       dc_identifier=etree.SubElement(oai_dc,"{"+dc+"}"+"identifier")
       dc_identifier.text=identifier[0]

    for each in creator_results:
       dc_creator=etree.SubElement(oai_dc,"{"+dc+"}"+"creator").text=each

    for each in title_results:
       dc_title=etree.SubElement(oai_dc,"{"+dc+"}"+"title").text=each

    if len(publisher) is not 0:
        dc_publisher=etree.SubElement(oai_dc,"{"+dc+"}"+"publisher").text=publisher[0]
    if len(publicationYear) is not 0:
        dc_publicationyear=etree.SubElement(oai_dc,"{"+dc+"}"+"date").text=publicationYear[0]

    for each in subject_results:
       etree.SubElement(oai_dc,"{"+dc+"}"+"subject").text=each

    if len(date_accepted) is not 0:
       dc_dateAcc=etree.SubElement(oai_dc,"{"+dcterms+"}"+"dateAccepted").text=date_accepted[0]

    if len(resourcetype) is not 0:
      dc_resource_type=etree.SubElement(oai_dc,"{"+dc+"}"+"type")
      dc_resource_type.text=resourcetype[0]

    if len(resourcetypegeneral) is not 0:
       dc_resource_type_general=etree.SubElement(oai_dc,"{"+dc+"}"+"type")
       dc_resource_type_general.set("{"+xsi+"}"+"type","dcterms:DCMIType")
       dc_resource_type_general.text=resourcetypegeneral[0].title()

    if len(alt_iden_type) is not 0 and alt_iden_type[0]=='citation':
       dc_citation=etree.SubElement(oai_dc,"{"+dcterms+"}"+"bibliographicCitation")
       dc_citation.text=alt_iden[0]

    for each in rel_iden_results:
       dc_re=etree.SubElement(oai_dc,"{"+dcterms+"}"+each[0])
       if each[2] is not 'NA':
           dc_re.text=each[2]

    if len(size) is not 0:
       dc_extent=etree.SubElement(oai_dc,"{"+dcterms+"}"+"extent").text=size[0]

    if len(right) is not 0:
        dc_rights=etree.SubElement(oai_dc, "{" + dc + "}" + "rights").text=right[0]
    if des is not '':
       etree.SubElement(oai_dc,"{"+dc+"}"+"description").text=des

    #write to file
    out=etree.tostring(record,pretty_print=True,encoding='UTF-8',xml_declaration=True)
    fout.write(out)
    fout.close()
