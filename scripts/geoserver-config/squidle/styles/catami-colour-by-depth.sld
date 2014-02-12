<sld:UserStyle xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml">
  <sld:Name>catami-colour-by-depth</sld:Name>
  <sld:Title/>
  <sld:FeatureTypeStyle>
    <sld:Name>catami-colour-by-depth</sld:Name>
    <sld:Title>catami-colour-by-depth</sld:Title>
    <sld:FeatureTypeName>Feature</sld:FeatureTypeName>
    <Rule>
       <PointSymbolizer>
         <Graphic>
           <Mark>
             <WellKnownName>circle</WellKnownName>
             <Fill>
               <CssParameter name="fill">
                 <ogc:Function name="Interpolate">
                   <!-- Property to transform -->
                   <ogc:PropertyName>depth</ogc:PropertyName>
          
                   <!-- Mapping curve definition pairs (input, output) -->
                   <ogc:Literal>22</ogc:Literal>
                   <ogc:Literal>#056837</ogc:Literal>
          
                   <ogc:Literal>27</ogc:Literal>
                   <ogc:Literal>#ffffbf</ogc:Literal>
          
                   <ogc:Literal>30</ogc:Literal>
                   <ogc:Literal>#a50026</ogc:Literal>
          
                   <!-- Interpolation method -->
                   <ogc:Literal>color</ogc:Literal>
          
                   <!-- Interpolation mode - defaults to linear -->
                 </ogc:Function>
               </CssParameter>
             </Fill>
           </Mark>
           <Size>12</Size>
         </Graphic>
      </PointSymbolizer>
    </Rule>
  </sld:FeatureTypeStyle>
</sld:UserStyle>