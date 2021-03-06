import json

from flask_wtf import Form
from wtforms import TextField, DecimalField, TextAreaField, DateField, FileField, RadioField, ValidationError, BooleanField, Field, SelectMultipleField, SelectField, FileField
from wtforms.validators import DataRequired, Regexp,  AnyOf
from wtforms.widgets import TextInput
from wtforms.widgets.core import HTMLString
from wtforms import Form as WTFForm



class TextFieldWithHelp(TextField):
    def __init__(self, *largs, **kargs):
        if "help" in kargs:
            self.help_text = kargs.pop("help")
        else:
            self.help_text = None
        super(TextFieldWithHelp, self).__init__(*largs, **kargs)

class TextAreaWithHelp(TextAreaField):
    def __init__(self, *largs, **kargs):
        if "help" in kargs:
            self.help_text = kargs.pop("help")
        else:
            self.help_text = None
        super(TextAreaWithHelp, self).__init__(*largs, **kargs)

class SearchQueryField(TextField):
    def process_formdata(self, values):
        if values:
            value = values[0]
            try:
                self.data = json.loads(value) # Make sure that it's in JSON
            except ValueError, e:
                raise ValidationError("Malformed JSON")
            # Check 'item' key
            if not self.data.has_key("item"):
                raise ValidationError("No 'item' in query.")
            if not self.data['item'] in ['User', 'Campaign', 'Category']:
                raise ValidationError("Can't query on '{}'".format(self.data['item']))
            # Check 'expand' key
            self.data['expand'] = self.data.get('expand', False)
            # The rest should be valid.
        else:
            self.data = ""

class DatePickerWidget(TextInput):
    """
    TextInput widget that adds a 'datepicker' class to the html input
    element; this makes it easy to write a jQuery selector that adds a
    UI widget for date picking.
    """
    def __call__(self, field, **kwargs):
        c = kwargs.pop('class', '') or kwargs.pop('class_', '')
        kwargs['class'] = u'datepicker %s' % c
        return super(DatePickerWidget, self).__call__(field, **kwargs)

class DatePickerField(DateField):
    widget = DatePickerWidget()


class CheckBoxSelectWidget(object):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """
    def __init__(self):
        pass

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []        
        for val, label, checked in field.iter_choices():
            if checked:
                html.append('<div class="checkbox"><label><input type="checkbox" name="{}" value="{}" checked="true"/>{}</label></div>'.format(field.name, val, label))
            else:
                html.append('<div class="checkbox"><label><input type="checkbox" name="{}" value="{}"/>{}</label></div>'.format(field.name, val, label))
        return HTMLString(''.join(html))

    # @classmethod
    # def render_option(cls, value, label, selected, **kwargs):
    #     options = dict(kwargs, value=value)
    #     if selected:
    #         options['selected'] = True
    #     return HTMLString('<option %s>%s</option>' % (html_params(**options), escape(text_type(label))))

class CheckBoxSelect(SelectMultipleField):
    widget = CheckBoxSelectWidget()



class CampaignForm(Form):
    category = RadioField('category', default = "single_lib", 
                          choices = [('single_lib', 'Organization/school raising books for a single library'),
                                     ('multiple_centres', 'You are an organization raising books for multiple centres'),
                                     ('reading_champ', 'You are a Reading Champion needing books for your sessions'),
                                     ('behalf', 'Individual raising books on behalf of a school/NGO/others')])
    name = TextField("Name of the Organisation/Individual")
    org_status = RadioField('org_status', default = "non_profit", 
                            choices = [("non_profit", "Registered non-profit"),
                                       ("section_25", "Section 25 Company"),
                                       ("private_school", "Private School"),
                                       ("budget_pvt_school", "Budget Private School (fee structure less than Rs.500 per month)"),
                                       ("govt_school", "Government School"),
                                       ("library", "Reading centre / library")])
    ho_address = TextField("Head office address")
    ho_phone = TextField("Head office phone number")
    ho_email = TextFieldWithHelp("Info Email ID", help="Please add the organisation info ID. It should not be individual specific.")
    website = TextField("Website")
    fb_page = TextField("Facebook page")
    blog = TextField("Blog Address")

    eightyg_cert = RadioField("80g certification", default = "Y", choices = [("Y","Y"), ("N","N")])

    creator_name = TextField("Your name")
    creator_position = TextField("Position in the organisation")
    creator_email = TextField("Your email address")
    creator_phone = TextField("Your phone number")
    shipping_name = TextField("Name")
    shipping_email = TextField("Shipping email address")
    shipping_phone = TextField("Phone number")

    how_changed = TextAreaField("How it changed the lives of the children you worked with.")

    children_number = TextField("Number of children that you/your organization impacts")
    children_age = TextField("Age group of children you impact")
    
    children_special = CheckBoxSelect("Do you/your organization do any work for following (check all that apply):", 
                                      default = "special_needs",
                                      choices = [("special_needs", "Children with special needs"),
                                                 ("tribal", "Children living in tribal areas"),
                                                 ("xxx", "Children XXX")])

    library = TextField("Books for a a library")
    bookbag = TextField("Books in a bag")
    prize = TextField("Books as a prize")
    reading = TextField("Books for reading sessions")
    language = SelectField("language", 
                           default = "Hindi",
                           choices = [("Hindi","Hindi"),
                                      ("English","English"),
                                      ("Marathi","Marathi"),
                                      ("Telugu","Telugu"),
                                      ("Gujarati","Gujarati"),
                                      ("Malayalam","Malayalam")])
    slider1 = TextField("")
    slider2 = TextField("")
    slider3 = TextField("")
    slider4 = TextField("")
    slidertotal = TextField("")

    impact = RadioField("Impact", 
                        default = "less100",
                        choices = [("less100", "Less than 100"),
                                   ("b100-250", "101 to 250"),
                                   ("b251-500", "251 to 500"),
                                   ("above500", "Above 500")])
    days = SelectField("duration", 
                       default = "1",
                       choices = [(str(x), str(x)) for x in range(1,46)])
    
    
    image = FileField()
    video = FileField()

    bookLanguages = SelectMultipleField("language", 
                                        default = "0",
                                        choices = [("0","All Languages"),
                                                   ("Assamese","Assamese"),
                                                   ("Bengali","Bengali"),
                                                   ("Gujarathi","Gujarathi"),
                                                   ("Hindi","Hindi"),
                                                   ("Kannada","Kannada"),
                                                   ("Konkani","Konkani"),
                                                   ("Malayalam","Malayalam"),
                                                   ("Marathi","Marathi"),
                                                   ("Oriya","Oriya"),
                                                   ("Punjabi","Punjabi"),
                                                   ("Tamil","Tamil"),
                                                   ("Telugu","Telugu")])

    stateCity = SelectMultipleField("states",
                                    default = "2169",
                                    choices = [("2169","Andhra Pradesh"),
                                               ("2196","Arunachal Pradesh"),
                                               ("2170","Assam"),
                                               ("2171","Bihar"),
                                               ("5267","Chhattisgarh"),
                                               ("2174","Delhi"),
                                               ("2199","Goa"),
                                               ("2175","Gujarat"),
                                               ("2176","Haryana"),
                                               ("2177","Himachal Pradesh"),
                                               ("2178","Jammu and Kashmir"),
                                               ("5268","Jharkhand"),
                                               ("2185","Karnataka"),
                                               ("2179","Kerala"),
                                               ("2181","Madhya Pradesh"),
                                               ("2182","Maharashtra"),
                                               ("2183","Manipur"),
                                               ("2184","Meghalaya"),
                                               ("2197","Mizoram"),
                                               ("2186","Nagaland"),
                                               ("2187","Orissa"),
                                               ("2189","Punjab"),
                                               ("2190","Rajasthan"),
                                               ("2195","Sikkim"),
                                               ("2191","Tamil Nadu"),
                                               ("2192","Tripura"),
                                               ("5269","UNION TERRITORY"),
                                               ("2193","Uttar Pradesh"),
                                               ("5259","Uttaranchal"),
                                               ("2194","West Bengal")])
    
    projectTitle = TextFieldWithHelp("Project Title", help="Enter Project Title (Max of 80 characters)")
    description = TextAreaWithHelp("Short description", help="Shorter is better - You will be able to explain more in your main pitch text 160 characters")
    introduce = TextAreaField()
    describe = TextAreaField()
    express = TextAreaField()

    explain = TextAreaField()
    perks = TextAreaField()
    describeFunds = TextAreaField()


    projectValue=TextAreaField()
    trackRecord=TextAreaField()
    trust=TextAreaField()
    stories=TextAreaField()

    campaignNoise = TextAreaField()
    tools = TextAreaField()

    trackingID = TextField("Enter tracking Id here")
    options = RadioField(default = "addPhoto", 
                         choices= [("addPhoto", "Add Photos"),
                                   ("addAlbum", "Add Albums"),
                                   ("addVideo", "Add Videos")])



class CategoryForm(Form):
    name = TextField('name', validators = [DataRequired()])
    icon = FileField('icon')

    # campaigns = relationship("Campaign", secondary = category_campaign_table, backref = "categories")

class SearchForm(Form):
    query = SearchQueryField("query")
