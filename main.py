from guide_generator import GuideGenerator
from guide_packager import GuidePackager

if __name__ == '__main__':
    guide_name = input('Guide name: ').lower().replace(' ', '_')
    if not guide_name:
        guide_name = 'dummy'

    guide_path = GuideGenerator.generate(guide_name)
    GuidePackager.pack(guide_name, guide_path)
