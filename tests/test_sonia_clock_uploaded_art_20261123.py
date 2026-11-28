"""Owner artwork stays archived while the prior in-game clock is restored."""
import pathlib
import unittest
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
ART=ROOT/'web/assets/original-ui/sonia_clock_ornate_20261123.webp'
JS=ROOT/'web/events.js'
CSS=ROOT/'web/events.css'
HTML=ROOT/'web/index.html'

class SoniaOwnerClockArt(unittest.TestCase):
    def test_original_uploaded_design_is_transparent_outside_and_clean(self):
        self.assertTrue(ART.is_file())
        with Image.open(ART) as im:
            self.assertEqual(im.size,(640,640))
            self.assertEqual(im.mode,'RGBA')
            alpha=im.getchannel('A')
            self.assertEqual(alpha.getpixel((0,0)),0)
            self.assertEqual(alpha.getpixel((639,0)),0)
            self.assertEqual(alpha.getpixel((0,639)),0)
            self.assertEqual(alpha.getpixel((639,639)),0)
            self.assertEqual(alpha.getpixel((555,545)),0)
            self.assertEqual(alpha.getpixel((585,600)),0)
            self.assertEqual(alpha.getpixel((320,320)),255)
            self.assertGreater(sum(alpha.histogram()[250:]),190000)

    def test_owner_asset_retained_but_clock_reverted_by_request(self):
        js=JS.read_text()
        clock=js[js.index(' function soniaClockFace('):js.index(' function eventPrizeImage(')]
        self.assertNotIn('sonia_clock_ornate_20261123.webp',clock)
        self.assertNotIn('sf-clock-ornate',clock)
        self.assertIn("el('div','sf-clock-hand')",clock)
        self.assertIn("el('div','sf-clock-center')",clock)
        self.assertIn("el('div','sf-clock-marks')",clock)
        self.assertIn("el('div','sf-clock-crown')",clock)
        self.assertIn('soniaClockIndex*60',clock)
        self.assertIn('i===soniaClockIndex',clock)
        style=CSS.read_text()
        self.assertNotIn('sf-clock-ornate',style)
        self.assertIn('sf-clock-prize.selected',style)
        self.assertIn('prefers-reduced-motion',style)
        html=HTML.read_text()
        self.assertIn('events.js?v=20261123-sonia-classic-polish-r10',html)
        self.assertIn('events.css?v=20261123-sonia-classic-polish-r10',html)

if __name__=='__main__': unittest.main()
