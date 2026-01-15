<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="tei">

    <xsl:output method="html" indent="yes" encoding="UTF-8"/>

    <xsl:template match="/">
        <html>
            <head>
                <title>Scott Pilgrim Scene Analysis</title>
                <style>
                    body { 
                        font-family: 'Courier New', monospace;
                        max-width: 800px; 
                        margin: 40px auto; 
                        line-height: 1.6; 
                        background-color: #f9f9f9;
                        color: #333;
                    }
                    .header-box { 
                        background: #fff; 
                        padding: 20px; 
                        border: 1px solid #ddd; 
                        margin-bottom: 40px; 
                        border-radius: 8px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                    h1 { font-size: 1.5em; text-align: center; color: #d32f2f; }
                    .meta-label { font-weight: bold; color: #555; }
                    .scene-head { 
                        font-weight: bold; 
                        text-decoration: underline; 
                        margin-top: 40px; 
                        margin-bottom: 20px;
                        text-transform: uppercase;
                    }
                    .stage { 
                        font-style: italic; 
                        color: #666; 
                        margin: 15px 0; 
                        display: block; 
                    }
                    .speaker { 
                        font-weight: bold; 
                        margin-top: 20px; 
                        display: block; 
                        text-align: center; 
                        text-transform: uppercase;
                    }
                    .dialogue { 
                        display: block; 
                        text-align: center; 
                        margin-bottom: 10px; 
                        max-width: 500px; 
                        margin-left: auto; 
                        margin-right: auto;
                    }
                    .page-break {
                        color: #aaa;
                        text-align: right;
                        font-size: 0.8em;
                        border-top: 1px dashed #ccc;
                        margin: 30px 0;
                        padding-top: 5px;
                    }
                    .entity-link { 
                        color: #c2185b; 
                        font-weight: bold; 
                        text-decoration: none; 
                        border-bottom: 1px dotted #c2185b; 
                    }
                    .entity-link:hover {
                        background-color: #fce4ec;
                        color: #880e4f;
                    }
                </style>
            </head>
            <body>
                <div class="header-box">
                    <h1><xsl:value-of select="//tei:titleStmt/tei:title"/></h1>
                    <p><span class="meta-label">Project Scope:</span> <xsl:value-of select="//tei:encodingDesc/tei:projectDesc/tei:p"/></p>
                    <p><span class="meta-label">Editorial Method:</span> <xsl:value-of select="//tei:encodingDesc/tei:editorialDecl/tei:p"/></p>
                    <p><span class="meta-label">Encoded By:</span> <xsl:value-of select="//tei:respStmt/tei:name"/></p>
                </div>
                <div class="script-content">
                    <xsl:apply-templates select="//tei:body"/>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="tei:head">
        <div class="scene-head"><xsl:apply-templates/></div>
    </xsl:template>

    <xsl:template match="tei:stage">
        <span class="stage">[<xsl:apply-templates/>]</span>
    </xsl:template>

    <xsl:template match="tei:speaker">
        <span class="speaker"><xsl:apply-templates/></span>
    </xsl:template>

    <xsl:template match="tei:p">
        <span class="dialogue"><xsl:apply-templates/></span>
    </xsl:template>

    <xsl:template match="tei:pb">
        <div class="page-break">Page <xsl:value-of select="@n"/></div>
    </xsl:template>

    <xsl:template match="tei:name">
        <xsl:choose>
            <xsl:when test="@ref">
                <xsl:variable name="firstWord" select="substring-before(concat(., ' '), ' ')"/>
                
                <xsl:variable name="formattedLink" select="concat(substring($firstWord, 1, 1), translate(substring($firstWord, 2), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))"/>

                <a class="entity-link" target="_blank">
                    <xsl:attribute name="href">
                        <xsl:value-of select="concat('https://scottpilgrim.fandom.com/wiki/', $formattedLink )"/>
                    </xsl:attribute>
                    <xsl:apply-templates/>
                </a>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>