# coding: utf-8

'''
Created on 14/06/2012

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

@author: Diego Navarro Mellén
'''


def xml2dict(tree, encoding='utf-8'):
    '''
    Converts an lxml etree object to Python dictionary
    '''
    
    def recursive_lookup(tree, encoding):
        children = tree.getchildren()
        if children:
            tag_names = set([e.tag for e in children 
                                if type(e.tag) is str])
            aux = {}
            for tag in tag_names:
                childs = tree.findall(tag)
                if len(childs) > 1:
                    aux[tag] = [recursive_lookup(c, encoding) for c in childs]
                else:
                    aux[tag] = recursive_lookup(childs[0], encoding)
            return aux
        else:
            return unicode(tree.text).encode(encoding)
 
    return {tree.tag: recursive_lookup(tree, encoding)}
 
    
def xml2json(tree):
    '''
    Converts an lxml etree to JSON
    '''
        
    import json
    return json.dumps(xml2dict(tree))

    
        