from pyramid.asset import package_path, resolve_asset_spec
import pystache
import os

class MustacheRendererFactory(object):
  def __init__(self, info):
    self.info = info

  def __call__(self, value, system):
    package, filename = resolve_asset_spec(self.info.name)
    template = os.path.join(package_path(self.info.package), filename)
    template_fh = open(template)
    template_stream = template_fh.read()
    template_fh.close()
    r = pystache.Renderer(
        search_dirs=[os.path.join(package_path(self.info.package), 'templates')])
    return r.render(template_stream, value)
